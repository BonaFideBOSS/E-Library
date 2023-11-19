from flask import Blueprint, render_template, request, session, abort, send_file
from . import db
from bson import ObjectId
from .helpers import db_searcher, get_file

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
    search = request.args.get("search", default=None, type=str)
    query = {"category_id": ObjectId(category_id)} if category_id else {}
    if search:
        search = db_searcher(["title", "author"], search)
        query.update(search)
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


@views.route("/books/<book_id>/download/", methods=["POST"])
def download_book(book_id):
    if "user" not in session:
        abort(404)
    book = db.Books.find_one({"_id": ObjectId(book_id)})
    file = get_file(book["book"])
    return send_file(
        file,
        download_name=f"{book['title']}.pdf",
        mimetype="application/pdf",
        as_attachment=True,
    )


@views.route("/books/update-stats/", methods=["POST"])
def update_book_stats():
    book_id = request.form.get("book_id")
    stats = request.form.get("stats")
    if book_id and stats in ["view", "download"]:
        db.Books.find_one_and_update(
            {"_id": ObjectId(book_id)},
            {"$inc": {f"{stats}_count": 1}},
        )
    return "", 200


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
