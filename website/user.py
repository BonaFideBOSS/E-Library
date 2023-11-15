from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db
from .forms import AccountForm
from .helpers import encrypt_message, upload_image_to_cloud
from datetime import datetime
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
    return render_template("user/bookmarks.html")


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
            avatar_url = upload_image_to_cloud(data["avatar"], form.username.data)
            data["avatar"] = avatar_url if avatar_url else user["avatar"]
        else:
            data["avatar"] = user["avatar"]

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
