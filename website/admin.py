from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from . import db

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
