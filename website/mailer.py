from flask import copy_current_request_context, request
from . import mail
from . import db
from flask_mail import Message
from .helpers import generate_token
import threading

db = db.db


def send_email_verification_mail(user_email: str):
    @copy_current_request_context
    def send_mail(to):
        token = generate_token()
        user = db.Users.find_one_and_update({"email": to}, {"$set": {"token": token}})

        if user:
            v_link = f"{request.host_url}verify-email?_id={user['_id']}&token={token}"
            email = Message("Email Verification", recipients=[to])
            email.html = f"""
            <p>Use the link below to verify your email:</p>
            <h1><a href="{v_link}">Click here to verify</a></h1>
            """
            mail.send(email)

    threading.Thread(target=send_mail, args=(user_email,)).start()


def send_password_reset_mail(user_email: str):
    @copy_current_request_context
    def send_mail(to):
        token = generate_token()
        user = db.Users.find_one_and_update({"email": to}, {"$set": {"token": token}})

        if user:
            v_link = f"{request.host_url}reset-password?_id={user['_id']}&token={token}"
            email = Message("Reset Password", recipients=[to])
            email.html = f"""
            <p>Use the link below to reset your password:</p>
            <h1><a href="{v_link}">Click here to reset your password</a></h1>
            <p>Please ignore this email if it wasn't requested by you.</p>
            """
            mail.send(email)

    threading.Thread(target=send_mail, args=(user_email,)).start()
