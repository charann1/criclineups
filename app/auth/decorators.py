from functools import wraps
from flask import abort, redirect, Markup
from flask.helpers import flash
from flask_login import current_user
from app.auth.models import Permission


def anonymous_required(url="/", message=""):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                flash(Markup(message), "primary")
                return redirect(url)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role.name not in roles:
                flash("You do not have permission to do that.", "primary")
                return redirect("/")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                flash("You do not have permission to do that.", "primary")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def unreachable(f):
    @wraps(f)
    def wrapper():
        def f(): return redirect("/")
        return f()

    return wrapper
