from flask import Blueprint, render_template
from . import db
from bson import ObjectId

db = db.db
views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/categories/")
def categories():
    pipeline = [
        {"$sort": {"category": 1}},
        {
            "$lookup": {
                "from": "Books",
                "localField": "_id",
                "foreignField": "category_id",
                "as": "books",
            }
        },
        {"$addFields": {"book_count": {"$size": "$books"}}},
    ]
    categories = db.Categories.aggregate(pipeline)
    return render_template("categories.html", categories=categories)


@views.route("/books/")
@views.route("/books/<category_id>/")
def books(category_id=None):
    query = {"category_id": ObjectId(category_id)} if category_id else {}
    books = list(db.Books.find(query))
    return render_template("books.html", books=books)


@views.route("/books/<book_id>")
def view_book(book_id):
    pipeline = [
        {"$match": {"_id": ObjectId(book_id)}},
        {
            "$lookup": {
                "from": "Categories",
                "localField": "category_id",
                "foreignField": "_id",
                "as": "category",
            }
        },
    ]
    book = list(db.Books.aggregate(pipeline))[0]
    return render_template("book-details.html", book=book)


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
