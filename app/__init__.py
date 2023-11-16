import logging
from flask import Flask
from config import Config
from logging.handlers import SMTPHandler
from app.auth.models import User, Role, Token
from app.cricket.models import Country, Team, PlayerType, PlayerKind, PlayerStatus, FantasyPlayer, FantasyTeam
from app.cmd import clear, del_tokens, reset, roles, update_players
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import (
    db,
    mail,
    csrf,
    login_manager,
    migrate,
    MigrateCommand,
    bootstrap
)
from data import players


def create_app(testing=False):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config.from_pyfile("settings.py", silent=True)

    middleware(app)
    blueprints(app)
    commands(app)
    extensions(app)
    authentication(app)
    shell_context(app)

    return app


def blueprints(app):

    from app.auth import auth
    from app.pages import pages
    from app.cricket import game
    from app.errors import errors

    app.register_blueprint(pages)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(game, url_prefix="/game")
    app.register_blueprint(errors, url_prefix="/errors")


def commands(app):
    app.cli.add_command(clear)
    app.cli.add_command(del_tokens)
    app.cli.add_command(reset)
    app.cli.add_command(roles)
    app.cli.add_command(update_players)
    app.cli.add_command("db", MigrateCommand)


def extensions(app):
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)


def authentication(app):

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "primary"
    login_manager.refresh_view = "auth.authenticate"
    login_manager.needs_refresh_message = (
        "To protect your account, please reauthenticate to access this page."
    )
    login_manager.needs_refresh_message_category = "primary"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


def shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
            "Role": Role,
            "Token": Token,
            "Country": Country,
            "Team": Team,
            "PlayerType": PlayerType,
            "PlayerKind": PlayerKind,
            "PlayerStatus": PlayerStatus,
            "FantasyPlayer": FantasyPlayer,
            "FantasyTea": FantasyTeam,
            "players": players
        }


def middleware(app):
    app.wsgi_app = ProxyFix(app.wsgi_app)
