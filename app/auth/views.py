from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    confirm_login,
    login_required,
    fresh_login_required,
)
from app.auth.forms import (
    LoginForm,
    AuthenticateForm,
    RegistrationForm,
    ProfileForm,
    RecoveryForm,
    ResetPasswordForm,
)
from app.lib.urls import safe_next_url
from app.auth.models import User, Token
from app.extensions import db
from app.auth.email import send_email
from app.auth.decorators import anonymous_required


auth = Blueprint("auth", __name__, template_folder="templates")


@auth.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and request.endpoint
        and request.blueprint != "auth"
        and request.endpoint != "static"
    ):
        current_user.ping(request.remote_addr)
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
@login_required
def unconfirmed():
    if not current_user.is_authenticated or current_user.confirmed:
        return redirect(url_for("pages.home"))
    return render_template("auth/unconfirmed.html")


@auth.route("/confirm")
@login_required
def resend_confirmation():
    current_user.initialize_email_request(
        current_user.email, subject="Confirm Your Account", template="auth/mail/confirm"
    )
    flash("A new confirmation email has been sent to you by email.", "primary")
    return redirect(url_for("pages.home"))


@auth.route("/confirm/<token>")
def confirm(token):
    t = Token.query.filter_by(key=token).first()
    if not t.expired:
        payload = Token.deserialize_token(token)
        user = User.query.get(payload.get("user_id"))
        if user and not user.confirmed:
            user.confirmed = True
            t.expired = True
            db.session.commit()
            flash("You have confirmed your account. Thanks!", "primary")
        else:
            flash("You have already confirmed your account.", "primary")
            return redirect(url_for("pages.home"))
    else:
        flash("Your email verification link is invalid or has expired!", "primary")
    return redirect(url_for("pages.home"))


@auth.route("/login", methods=["GET", "POST"])
@anonymous_required(
    message='You are already logged in. Click here to <a class="anchor-primary" href="/auth/logout">Logout</a>'
)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(request.form.get("email"))
        if user and user.authenticated(password=request.form.get("password")):
            if login_user(user, remember=form.remember.data) and user.is_active():
                next_url = request.args.get("next")
                if next_url:
                    return redirect(safe_next_url(next_url))
                flash("Login successful!", "primary")
                return redirect(url_for("pages.home"))
        else:
            flash("Bad credentials! Please try again.", "primary")
            return redirect(url_for("auth.login"))
    return render_template("auth/login.html", form=form)


@auth.route("/authenticate", methods=["GET", "POST"])
def authenticate():
    form = AuthenticateForm()
    form.email.data = current_user.email
    form.email.render_kw = {"disabled": "disabled"}
    if form.validate_on_submit():
        if current_user.authenticated(password=request.form.get("password")):
            confirm_login()
            next_url = request.args.get("next")
            if next_url:
                return redirect(safe_next_url(next_url))
            return redirect(url_for("pages.home"))
        else:
            flash("Username or password is incorrect.", "primary")
            return redirect(url_for("auth.authenticate"))
    return render_template("auth/authenticate.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been loggedout!", "primary")
    return redirect(url_for("pages.home"))


@auth.route("/register", methods=["GET", "POST"])
@anonymous_required(
    message='You are already logged in. Click here to <a class="anchor-primary" href="/auth/logout">Logout</a>'
)
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.lower().strip(), email=form.email.data.lower().strip()
        )
        user.encrypt_password(request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        user.initialize_email_request(
            user.email, subject="Confirm Your Account", template="auth/mail/confirm"
        )
        login_user(user)
        flash("A confirmation email has been sent to you by email.", "primary")
        return redirect(url_for("pages.home"))
    return render_template("auth/register.html", form=form)


@auth.route("/profile", methods=["GET", "POST"])
@fresh_login_required
def profile():
    if not current_user.confirmed:
        return redirect(url_for("auth.unconfirmed"))
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if current_user.authenticated(password=form.current_password.data):
            if form.name.data and not current_user.name == form.name.data:
                current_user.name = form.name.data
            if form.email.data and not current_user.email == form.email.data:
                new_email = form.email.data.lower()
                current_user.initialize_email_request(
                    email=new_email,
                    subject="Confirm Your Email Address",
                    template="auth/mail/change_email",
                )
                flash(
                    "An email with instructions to confirm your new email address has been sent to you.",
                    "info",
                )
            if (
                form.new_password.data
                and form.confirm_password.data
                and form.new_password.data == form.confirm_password.data
            ):
                current_user.encrypt_password(form.new_password.data)
            db.session.commit()
            flash("Your credentials has been updated!", "primary")
            return redirect(url_for("auth.profile"))
        else:
            flash("Wrong Password.", "primary")
    return render_template("auth/profile.html", form=form)


@auth.route("/change_email/<token>")
def change_email(token):
    payload = Token.deserialize_token(token)
    email = payload.get("email")
    user = User.query.get(payload.get("user_id"))
    t = Token.query.filter_by(key=token).first()
    if t and not t.expired and email and user:
        user.email = email
        t.expired = True
        db.session.commit()
        flash("Your email address has been updated.", "primary")
        return redirect(url_for("pages.home"))
    flash("Your email verification link is invalid or has expired!", "primary")
    return redirect(url_for("pages.home"))


@auth.route("/recovery", methods=["GET", "POST"])
@anonymous_required(
    message='You are already logged in. Click here to <a class="anchor-primary" href="/auth/logout">Logout</a>'
)
def request_password():
    form = RecoveryForm()
    if form.validate_on_submit():
        flash(
            "If that email address is in our database, we will send you an email to reset your password.",
            "primary",
        )
        user = User.find_by_email(request.form.get("email").lower())
        if user:
            user.initialize_password_request()
        return redirect(url_for("auth.request_password"))
    return render_template("auth/recovery.html", form=form)


@auth.route("/recovery/<token>", methods=["GET", "POST"])
@anonymous_required()
def reset_password(token):
    form = ResetPasswordForm()
    payload = Token.deserialize_token(token)
    user = User.query.get(payload.get("user_id"))
    t = Token.query.filter_by(key=token).first()
    if t and not t.expired and user:
        if form.validate_on_submit():
            user.encrypt_password(form.new_password.data)
            t.expired = True
            db.session.commit()
            flash("Your password has been reset.", "primary")
            return redirect(url_for("auth.login"))
    else:
        flash("Your password reset link is invalid or has expired", "primary")
        return redirect(url_for("pages.home"))
    return render_template("auth/reset_password.html", form=form)
