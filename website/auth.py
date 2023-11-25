from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from . import db
from .forms import RegisterForm, LoginForm, ForgotPassword, ResetPassword
from .helpers import encrypt_message
from bson import ObjectId
from datetime import datetime
from .mailer import send_email_verification_mail, send_password_reset_mail

db = db.db
auth = Blueprint("auth", __name__)
DEFAULT_AVATAR = "/assets/img/user.jpg"


@auth.before_request
def is_user_logged_in():
    if "user" in session and request.endpoint in ["auth.login", "auth.register"]:
        return redirect(url_for("views.home"))


# Function to add user to the session
def add_user_to_session(user: dict, remember: bool = False):
    user["_id"] = str(user["_id"])
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
        user["avatar"] = DEFAULT_AVATAR
        db.Users.insert_one(user)
        send_email_verification_mail(user["email"])
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


@auth.route("/resend-email-verification-mail", methods=["POST"])
def resend_email_verification_mail():
    user_email = session["user"]["email"]
    send_email_verification_mail(user_email)
    return ""


@auth.route("/logout/", methods=["POST"])
def logout():
    session.pop("user", None)
    flash("Successfully logged out.")
    return redirect(request.referrer)


@auth.route("/verify-email/")
def verify_email():
    user_id = request.args.get("_id")
    token = request.args.get("token")

    verified = False
    if user_id and token:
        user = db.Users.find_one_and_update(
            {"_id": ObjectId(user_id), "token": token},
            {"$set": {"verified": True}},
            return_document=True,
        )
        if user:
            verified = True
            add_user_to_session(user)
        return render_template("auth/verify-email.html", verified=verified)

    else:
        return redirect(url_for("views.home"))


@auth.route("/forgot-password/", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPassword()

    if form.validate_on_submit():
        send_password_reset_mail(form.email.data)
        flash("Password reset link sent to your email.")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot-password.html", form=form)


@auth.route("/reset-password/", methods=["GET", "POST"])
def reset_password():
    user_id = request.args.get("_id")
    token = request.args.get("token")
    form = ResetPassword(user_id=user_id, token=token)

    if form.validate_on_submit():
        db.Users.find_one_and_update(
            {"_id": ObjectId(user_id), "token": token},
            {"$set": {"password": encrypt_message(form.password.data)}},
        )
        flash("Your password has been successfully updated.")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset-password.html", form=form)
