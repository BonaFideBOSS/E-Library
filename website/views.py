from flask import Blueprint, render_template
from . import db

db = db.db
views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/categories/")
def categories():
    return render_template("categories.html")


@views.route("/books/")
def books():
    return render_template("books.html")


@views.route("/about/")
def about():
    return render_template("about.html")


@views.route("/contact/")
def contact():
    return render_template("contact.html")


@views.route("/terms/")
def terms():
    return render_template("terms.html")


@views.route("/privacy/")
def privacy():
    return render_template("privacy.html")


@views.route("/ping/")
def ping():
    return "This site is live!", 200
