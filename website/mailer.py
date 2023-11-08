from flask import copy_current_request_context, request
from . import mail
from . import db
from flask_mail import Message
from .helpers import generate_token
import threading

db = db.db


def mail_otp(user_email: str):
    @copy_current_request_context
    def send_mail(to):
        otp = generate_token()
        user = db.Users.find_one_and_update({"email": to}, {"$set": {"otp": otp}})

        if user:
            v_link = f"{request.host_url}verify-email?_id={user['_id']}&otp={otp}"
            email = Message("OTP", recipients=[to])
            email.html = f"""
            <p>Use the link below to verify your email:</p>
            <h1><a href="{v_link}">Click here to verify</a></h1>
            """
            mail.send(email)

    threading.Thread(target=send_mail, args=(user_email,)).start()
