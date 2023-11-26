from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db
from .forms import AccountForm
from .helpers import encrypt_message, upload_image_to_cloud
from bson import ObjectId
from .auth import add_user_to_session
from .mailer import send_email_verification_mail

db = db.db
user = Blueprint("user", __name__)


@user.before_request
def is_user_logged_in():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    else:
        user = db.Users.find_one({"_id": ObjectId(session["user"]["_id"])})
        if user:
            add_user_to_session(user)
        else:
            session.pop("user", None)
            return redirect(url_for("auth.login"))


@user.route("/bookmarks")
def bookmarks():
    user_id = ObjectId(session["user"]["_id"])
    user = db.Users.find_one({"_id": user_id})
    bookmarks = user["bookmarks"] if "bookmarks" in user else []
    bookmarks = [ObjectId(book) for book in bookmarks]
    books = list(db.Books.find({"_id": {"$in": bookmarks}}))
    return render_template("user/bookmarks.html", books=books)


@user.route("/manage-bookmark", methods=["POST"])
def manage_bookmark():
    book_id = request.form.get("book_id")
    action = request.form.get("action")
    response = {"success": False}
    try:
        user = {"_id": ObjectId(session["user"]["_id"])}
        book_id = {"bookmarks": book_id}
        update_query = {"$addToSet": book_id} if action == "add" else {"$pull": book_id}
        user = db.Users.find_one_and_update(user, update_query, return_document=True)
        add_user_to_session(user)
        response["success"] = True
    except:
        pass
    return response


# Function to render user's account page
@user.route("/account", methods=["GET", "POST"])
def account():
    form = AccountForm()
    user = session["user"]

    if form.is_submitted():
        form.user_id.data = ObjectId(user["_id"])
        if not form.password.data:
            form.password.data = session["user"]["password"]

    if form.validate_on_submit():
        data = form.data
        data.pop("csrf_token")
        data.pop("user_id")

        if data["email"] != user["email"]:
            data["verified"] = False

        if data["password"] != user["password"]:
            data["password"] = encrypt_message(data["password"])

        if data["avatar"]:
            # Upload avatar to cloud
            avatar_url = upload_image_to_cloud(data["avatar"], form.username.data)
            data["avatar"] = avatar_url if avatar_url else user["avatar"]
        else:
            data["avatar"] = user["avatar"]

        # Update user details
        user = db.Users.find_one_and_update(
            {"_id": ObjectId(user["_id"])},
            {"$set": data},
            return_document=True,
        )
        add_user_to_session(user)
        if not user["verified"]:
            send_email_verification_mail(user["email"])
        flash("Successfully updated account details.")

    return render_template("user/account.html", form=form)


# Function to let user delete their account
@user.route("/delete-account", methods=["POST"])
def delete_account():
    try:
        user_id = ObjectId(session["user"]["_id"])
        db.Users.delete_one({"_id": user_id})
        session.pop("user", None)
        flash("Account successfully deleted!")
    except:
        flash("Failed to delete account.")
    return redirect(url_for("auth.login"))
