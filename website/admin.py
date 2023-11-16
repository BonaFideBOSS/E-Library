from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db
from functools import wraps
from bson import json_util, ObjectId
from .admin_forms import CategoryForm, NewCategoryForm, UserForm
from .helpers import encrypt_message, upload_image_to_cloud

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
    if not "staff" in userrolees:
        flash("You do not have enough permission to access this page.")
        return redirect(url_for("views.home"))


def authorize_roles(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not any(role in session["user"]["roles"] for role in roles):
                flash("You do not have enough permission to perform this action.")
                return redirect(url_for("admin.dashboard"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@admin.route("/")
def dashboard():
    data = {
        "categories": db.Categories.count_documents({}),
        "books": db.Books.count_documents({}),
        "users": db.Users.count_documents({}),
    }
    return render_template("admin/dashboard.html", data=data)


@admin.route("/categories")
def categories():
    return render_template("admin/categories.html")


@admin.route("/books")
def books():
    return render_template("admin/books.html")


@admin.route("/users")
def users():
    return render_template("admin/users.html")


@admin.route("/categories/new/", methods=["GET", "POST"])
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        data = form.data
        data.pop("category_id")
        data.pop("csrf_token")
        data.pop("submit")
        data["image"] = upload_image_to_cloud(data["image"], data["category"])
        db.Categories.insert_one(data)
        flash("Successfully created a new category")
        return redirect(url_for("admin.categories"))

    return render_template("admin/manage-category.html", form=form)


@admin.route("/categories/manage/<category_id>", methods=["GET", "POST"])
def manage_category(category_id):
    category = db.Categories.find_one({"_id": ObjectId(category_id)})
    form = CategoryForm(
        category_id=category["_id"],
        category=category["category"],
        icon=category["icon"],
        image=category["image"],
    )

    @authorize_roles("admin")
    def update_category():
        data = form.data
        data.pop("category_id")
        data.pop("csrf_token")
        data.pop("submit")
        if data["image"] != category["image"]:
            data["image"] = upload_image_to_cloud(data["image"], data["category"])
            form.image.data = data["image"]
        db.Categories.update_one(category, {"$set": data})
        flash("Details updated successfully!")

    if form.is_submitted():
        form.category_id.data = category["_id"]

    if form.validate_on_submit():
        update_category()

    return render_template("admin/manage-category.html", category=category, form=form)


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


@admin.route("/get-users", methods=["POST"])
def get_users():
    params = search_params("email")
    data = get_records("Users", params)
    return data


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
