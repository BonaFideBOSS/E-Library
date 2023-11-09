from . import db
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .helpers import encrypt_message
from bson import ObjectId

db = db.db


# Registration Form - Used to validate new account creation
class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Please enter a username."),
            Length(min=4, max=26, message="Username must be 4 to 26 characters long."),
        ],
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Please enter an email address."),
            Email(message="Please enter a valid email address."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
    )

    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if user:
            raise ValidationError("This email is already is use.")


# Login Form - Used to validate existing account credentials
class LoginForm(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(message="Please enter your email address.")]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Please enter your password.")]
    )

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        user = get_user_by_email(self.email.data)

        if not user:
            self.email.errors.append("Email not found.")
            return False

        password = encrypt_message(self.password.data)
        if password != user["password"]:
            self.password.errors.append("Password is incorrect.")
            return False

        return True


class ForgotPassword(FlaskForm):
    email = EmailField(
        "Email", validators=[DataRequired(message="Please enter your email address.")]
    )

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        user = get_user_by_email(self.email.data)
        if not user:
            self.email.errors.append("Email not found.")
            return False

        return True


class ResetPassword(FlaskForm):
    user_id = HiddenField()
    token = HiddenField()

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=8, message="Password must be at least 8 characters long."),
        ],
    )

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        user = {}
        try:
            user = db.Users.find_one({"_id": ObjectId(self.user_id.data)})
        except:
            pass

        if not user or self.token.data != user["token"]:
            self.password.errors.append("Failed to reset password.")
            return False

        return True


def get_user_by_email(email: str):
    return db.Users.find_one({"email": email})
