from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional, Regexp
from app.lib.forms import ModelForm
from app.lib.validations import check_password
from app.auth.models import User
from flask_login import current_user


class LoginForm(FlaskForm):
    email = StringField("Email", [DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class AuthenticateForm(FlaskForm):
    email = StringField("Email", [DataRequired(), Email()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Verify")


class RegistrationModelForm(ModelForm):
    class Meta:
        model = User
        only = ["name", "email"]
        validators = {"email": [Email()]}


class RegistrationForm(RegistrationModelForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(8, 128),
            EqualTo("confirm_password", message=""),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(8, 128),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Sign up")


class ProfileForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[Optional(), Length(2, 128)],
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email()],
    )
    new_password = PasswordField(
        "New Password",
        validators=[
            Optional(),
            Length(8, 128),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            Optional(),
            Length(8, 128),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    current_password = PasswordField(
        "Current Password",
        render_kw={"class": "password-field"},
        validators=[
            DataRequired(),
            check_password,
        ],
    )
    submit = SubmitField("Update")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class RecoveryForm(FlaskForm):
    email = StringField("Email", [DataRequired(), Email()])
    submit = SubmitField("Submit")


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(8, 128),
            EqualTo("confirm_password", message=""),
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            Length(8, 128),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Submit")
