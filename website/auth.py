from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from . import db
from .forms import RegisterForm, LoginForm, encrypt_message
from bson import json_util, ObjectId
from datetime import datetime
from .mailer import mail_otp

db = db.db
auth = Blueprint("auth", __name__)


@auth.before_request
def is_user_logged_in():
    if "user" in session and request.endpoint in ["auth.login", "auth.register"]:
        return redirect(url_for("views.home"))


def add_user_to_session(user: dict, remember: bool = False):
    user["_id"] = json_util.dumps(user["_id"]).split('"')[3]
    session["user"] = user
    session.permanent = remember


@auth.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = form.data
        user.pop("csrf_token")
        user["password"] = encrypt_message(user["password"])
        user["created_on"] = datetime.utcnow()
        user["verified"] = False
        user["avatar"] = "/assets/img/user.jpg"
        db.Users.insert_one(user)
        mail_otp(user["email"])
        add_user_to_session(user)
        flash("Successfully created a new account.")
        return redirect(url_for("views.home"))

    return render_template("auth/register.html", form=form)


@auth.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.Users.find_one({"email": form.email.data})
        remember = True if request.form.get("remember") == "on" else False
        add_user_to_session(user, remember)
        flash("Successfully logged in.")
        return redirect(url_for("views.home"))

    return render_template("auth/login.html", form=form)


@auth.route("/resend-otp/", methods=["POST"])
def resend_otp():
    reason = request.args.get("reason")
    user_email = session["user"]["email"]
    if reason == "email":
        mail_otp(user_email)
    return ""


@auth.route("/logout/", methods=["POST"])
def logout():
    session.pop("user", None)
    flash("Successfully logged out.")
    return redirect(request.referrer)


@auth.route("/verify-email/")
def verify_email():
    user_id = request.args.get("_id")
    otp = request.args.get("otp")

    verified = False
    if user_id and otp:
        user = db.Users.find_one_and_update(
            {"_id": ObjectId(user_id), "otp": otp},
            {"$set": {"verified": True}},
            return_document=True,
        )
        if user:
            verified = True
            add_user_to_session(user)
        return render_template("auth/verify-email.html", verified=verified)

    else:
        return redirect(url_for("views.home"))
