# Importing required modules
from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db
from functools import wraps
from bson import json_util, ObjectId
from .admin_forms import CategoryForm, NewCategoryForm, BooksForm, NewBookForm, UserForm
from .helpers import encrypt_message, upload_image_to_cloud, upload_pdf_to_cloud

db = db.db
admin = Blueprint("admin", __name__)


# Function to check if user is admin
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
    if not "staff" in userrolees:
        flash("You do not have enough permission to access this page.")
        return redirect(url_for("views.home"))


# Decorator to authorize roles
def authorize_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user has any of the required roles
            if not any(role in session["user"]["roles"] for role in roles):
                flash("You do not have enough permission to perform this action.")
                return redirect(url_for("admin.dashboard"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Admin Dashboard
@admin.route("/")
def dashboard():
    # Getting documents count from the database
    data = {
        "categories": db.Categories.count_documents({}),
        "books": db.Books.count_documents({}),
        "users": db.Users.count_documents({}),
    }
    return render_template("admin/dashboard.html", data=data)


# Categories page
@admin.route("/categories")
def categories():
    return render_template("admin/categories.html")


# Books page
@admin.route("/books")
def books():
    return render_template("admin/books.html")


# Users page
@admin.route("/users")
def users():
    return render_template("admin/users.html")


# Page to create new category
@admin.route("/categories/new/", methods=["GET", "POST"])
def new_category():
    # Initialize the form
    form = NewCategoryForm()
    # Validate the form
    if form.validate_on_submit():
        data = form.data
        data.pop("category_id")  # remove id because it is auto generated
        data.pop("csrf_token")  # remove csrf_token
        data.pop("submit")  # remove submit button
        # Upload category cover image to cloud
        data["image"] = upload_image_to_cloud(data["image"], data["category"])
        # Save data to the database
        db.Categories.insert_one(data)
        flash("Successfully created a new category")
        return redirect(url_for("admin.categories"))

    return render_template("admin/manage-category.html", form=form)


# Page to manage categories
@admin.route("/categories/manage/<category_id>", methods=["GET", "POST"])
def manage_category(category_id):
    # Get category from Id
    category = db.Categories.find_one({"_id": ObjectId(category_id)})
    # Pass category details to form
    form = CategoryForm(
        category_id=category["_id"],
        category=category["category"],
        icon=category["icon"],
        image=category["image"],
    )

    # Authorize who can make changes to the category
    @authorize_roles("admin")
    def update_category():
        data = form.data
        data.pop("category_id")
        data.pop("csrf_token")
        data.pop("submit")
        # Check if new image is uploaded
        if data["image"] != category["image"]:
            # upload the new image to cloud
            data["image"] = upload_image_to_cloud(data["image"], data["category"])
            form.image.data = data["image"]
        # Update database
        db.Categories.update_one(category, {"$set": data})
        flash("Details updated successfully!")

    if form.is_submitted():
        form.category_id.data = category["_id"]

    if form.validate_on_submit():
        update_category()

    return render_template("admin/manage-category.html", category=category, form=form)


# New Book Page
@admin.route("/books/new/", methods=["GET", "POST"])
def new_book():
    # Initialize the form
    form = NewBookForm()

    # Validate the form on submit
    if form.validate_on_submit():
        data = form.data
        data.pop("book_id")
        data.pop("csrf_token")
        data.pop("submit")
        if data["type"] == "book":
            # Upload book to cloud
            data["book"] = upload_pdf_to_cloud(data["book"])
        data["category_id"] = ObjectId(data["category_id"])
        data["author"] = data["author"].split(",")
        # Upload cover to cloud
        data["cover"] = upload_image_to_cloud(data["cover"], data["title"])
        data["downloadable"] = eval(data["downloadable"])
        data["view_count"] = 0
        data["download_count"] = 0
        # Insert record to the database
        db.Books.insert_one(data)
        flash("Successfully added a new book.")
        return redirect(url_for("admin.books"))

    return render_template("admin/manage-books.html", form=form)


# Page to edit books and videos
@admin.route("/books/manage/<book_id>", methods=["GET", "POST"])
def manage_book(book_id):
    book = db.Books.find_one({"_id": ObjectId(book_id)})
    form = BooksForm(
        book_id=book["_id"],
        title=book["title"],
        type=book["type"],
        category_id=book["category_id"],
        year=book["year"],
        cover=book["cover"],
        author=",".join(book["author"]),
        publisher=book["publisher"],
        summary=book["summary"],
        downloadable=book["downloadable"],
        book=book["book"] if "book" in book else "",
        video=book["video"] if "video" in book else "",
    )

    @authorize_roles("admin")
    def update_book():
        data = form.data
        data.pop("book_id")
        data.pop("csrf_token")
        data.pop("submit")
        data["category_id"] = ObjectId(data["category_id"])
        data["author"] = data["author"].split(",")
        data["downloadable"] = eval(data["downloadable"])
        if data["book"] != book["book"]:
            data["book"] = upload_pdf_to_cloud(data["book"])
            form.book.data = data["book"]
        if data["cover"] != book["cover"]:
            data["cover"] = upload_image_to_cloud(data["cover"], data["title"])
            form.cover.data = data["cover"]
        db.Books.update_one(book, {"$set": data})
        flash("Details updated successfully!")

    if form.is_submitted():
        form.book_id.data = book["_id"]

    if form.validate_on_submit():
        update_book()

    return render_template("admin/manage-books.html", book=book, form=form)


# Page to manage users
@admin.route("/users/manage/<user_id>", methods=["GET", "POST"])
def manager_user(user_id):
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    form = UserForm(
        user_id=user["_id"],
        avatar=user["avatar"],
        username=user["username"],
        email=user["email"],
        verified=user["verified"],
        roles=",".join(user["roles"]) if "roles" in user else "",
    )

    @authorize_roles("admin")
    def update_user():
        data = form.data
        data.pop("user_id")
        data.pop("csrf_token")
        if data["password"]:
            data["password"] = encrypt_message(data["password"])
        else:
            data.pop("password")
        data["verified"] = eval(data["verified"])
        data["roles"] = data["roles"].split(",")
        db.Users.update_one(user, {"$set": data})
        flash("Details updated successfully!")

    if form.is_submitted():
        form.user_id.data = user["_id"]

    if form.validate_on_submit():
        update_user()

    return render_template("admin/manage-user.html", user=user, form=form)


# API to delete an item from the database
@admin.route("/database/<collection>/delete/<_id>", methods=["POST"])
@authorize_roles("admin")
def delete_db_record(collection: str, _id: ObjectId):
    if not (collection == "Users" and _id == "65512270765d2c3b115fa64e"):
        db[collection].delete_one({"_id": ObjectId(_id)})
        flash(f"Successfully deleted entry from the {collection} collection.")
    return redirect(url_for(f"admin.{collection.lower()}"))


# ===== APIs =====
@admin.route("/get-categories", methods=["POST"])
def get_categories():
    params = search_params("category")
    data = get_records("Categories", params)
    return data


@admin.route("/get-books", methods=["POST"])
def get_books():
    params = search_params("title")
    data = get_records("Books", params)
    return data


@admin.route("/get-users", methods=["POST"])
def get_users():
    params = search_params("email")
    data = get_records("Users", params)
    return data


# Function to get data from database based on the given parameters
def get_records(collection: str, params: dict):
    total_records = db[collection].count_documents({})
    filtered_records = db[collection].count_documents(params["search"])
    records = (
        db[collection]
        .find(params["search"])
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


# Function to get search parameters to filter out database records
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
