from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db
from .helpers import db_searcher
from bson import json_util

db = db.db
admin = Blueprint("admin", __name__)


@admin.before_request
def is_user_admin():
    userrolees = []

    # Check if user is logged in
    if not "user" in session:
        return redirect(url_for("auth.login"))

    # Check if user has any role
    if "roles" in session["user"]:
        userrolees = session["user"]["roles"]

    # Check if user has admin role
    if not "admin" in userrolees:
        flash("You do not have enough permission to access this page.")
        return redirect(url_for("views.home"))


@admin.route("/")
def dashboard():
    return render_template("admin/dashboard.html")


@admin.route("/categories")
def categories():
    return render_template("admin/categories.html")


@admin.route("/books")
def books():
    return render_template("admin/books.html")


@admin.route("/users")
def users():
    return render_template("admin/users.html")


@admin.route("/users", methods=["POST"])
def get_users():
    params = search_params("email")
    total_records = db.Users.count_documents({})
    filtered_records = db.Users.count_documents({})
    records = (
        db.Users.find(params["search"])
        .sort(params["order"], params["order_dir"])
        .skip(params["start"])
        .limit(params["length"])
    )
    data = {
        "draw": params["draw"],
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": records,
    }
    return json_util.dumps(data)


def search_params(field: str):
    draw = request.form.get("draw", default=1, type=int)
    start = request.form.get("start", default=0, type=int)
    order = request.form.get("order[0][column]", default=0, type=int)
    order_dir = request.form.get("order[0][dir]", default="asc", type=str)
    length = request.form.get("length", default=5, type=int)
    search = request.form.get("search[value]", default=None, type=str)
    if search:
        search = {
            "$and": [{field: {"$regex": i, "$options": "i"}} for i in search.split()]
        }
    else:
        search = {}
    order = request.form.get(f"columns[{order}][data]").split(".$")[0]
    order_dir = -1 if order_dir == "desc" else 1
    json = {
        "draw": draw,
        "start": start,
        "length": length,
        "order": order,
        "order_dir": order_dir,
        "search": search,
    }
    return json
