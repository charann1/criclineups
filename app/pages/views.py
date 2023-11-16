from flask import Blueprint, render_template

pages = Blueprint("pages", __name__, template_folder='templates')


@pages.route("/")
def home():
    return render_template("pages/index.html")
