import os
import click
from flask.cli import with_appcontext
from app.auth.models import Role, Token
from app.extensions import db
from data import players


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
d = os.path.join(basedir, "migrations")
f = os.path.join(basedir, "db.sqlite3")
ve = os.path.join(basedir, ".venv")


@click.command()
@with_appcontext
def roles():
    Role.insert_roles()


@click.command()
@with_appcontext
def del_tokens():
    Token.delete_tokens()


@click.command()
@with_appcontext
def roles():
    Role.insert_roles()


@click.command()
@with_appcontext
def update_players():
    db.session.bulk_save_objects(players)
    db.session.commit()


@click.command()
@with_appcontext
def clear():

    if os.path.isdir(d):
        if os.system("rm -r migrations"):
            raise RuntimeError("compile command failed")

    if os.path.isfile(f):
        if os.system("rm db.sqlite3"):
            raise RuntimeError("compile command failed")

    if os.system("find . -type f -name __init__.pyc -exec rm \{\} \\+"):
        raise RuntimeError("compile command failed")

    if os.system("find . -type d -name __pycache__ -exec rm -r \{\} \\+"):
        raise RuntimeError("compile command failed")

    if os.path.isdir(ve):
        if os.system("rm -r .venv"):
            raise RuntimeError("compile command failed")


@click.command()
@with_appcontext
def reset():

    if os.path.isdir(ve):
        if os.system("rm -r .venv"):
            raise RuntimeError("compile command failed")

    if os.path.isdir(d):
        if os.system("rm -r migrations"):
            raise RuntimeError("compile command failed")

    if os.path.isfile(f):
        if os.system("rm db.sqlite3"):
            raise RuntimeError("compile command failed")

    if os.system("find . -type f -name __init__.pyc -exec rm \{\} \\+"):
        raise RuntimeError("compile command failed")

    if os.system("find . -type d -name __pycache__ -exec rm -r \{\} \\+"):
        raise RuntimeError("compile command failed")

    if os.system("python3 -m venv .venv"):
        raise RuntimeError("compile command failed")

    if os.system("source .venv/bin/activate"):
        raise RuntimeError("compile command failed")

    if os.system("pip install -r requirements.txt"):
        raise RuntimeError("compile command failed")

    if os.system("flask db init"):
        raise RuntimeError("compile command failed")

    if os.system("flask db migrate -m 'intial migrations'"):
        raise RuntimeError("compile command failed")

    if os.system("flask db upgrade"):
        raise RuntimeError("compile command failed")

    if os.system("flask roles"):
        raise RuntimeError("compile command failed")

    if os.system("flask run"):
        raise RuntimeError("compile command failed")
