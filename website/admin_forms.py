from . import db
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SelectField,
    HiddenField,
    SubmitField,
)
from flask_wtf.file import FileField, FileAllowed, FileSize, FileRequired
from wtforms.validators import DataRequired, ValidationError

db = db.db
max_file_size = 32  # in MB
supported_filetypes = [
    "jpg",
    "png",
    "jpeg",
    "webp",
    "gif",
    "jfif",
    "avif",
    "bmp",
    "ico",
    "heic",
    "pdf",
]
file_validators = [
    FileAllowed(
        upload_set=supported_filetypes,
        message="This type of file is not supported",
    ),
    FileSize(
        max_size=max_file_size * 1024 * 1024,
        message=f"File size is too large. Max allowed: {max_file_size} MB",
    ),
]


class CategoryForm(FlaskForm):
    category_id = StringField("Category Id", render_kw={"disabled": True})
    category = StringField(
        "Category", validators=[DataRequired("Category title is required.")]
    )
    icon = StringField("Icon", validators=[DataRequired("Icon is required.")])
    image = FileField("Image", validators=file_validators)
    submit = SubmitField("Save Changes")

    def validate_category(self, category):
        query = {"category": category.data}
        query["_id"] = {"$ne": self.category_id.data}
        category = db.Categories.find_one(query)
        if category:
            raise ValidationError("This category is already defined.")


class NewCategoryForm(CategoryForm):
    category_id = HiddenField()
    image = FileField(
        "Image", validators=[FileRequired("An image is required.")] + file_validators
    )
    submit = SubmitField("Add New Category")


class UserForm(FlaskForm):
    user_id = StringField("User Id", render_kw={"disabled": True})
    avatar = StringField("Avatar", validators=[DataRequired("Avatar is required.")])
    username = StringField(
        "Username", validators=[DataRequired("Username cannot be blank.")]
    )
    email = EmailField("Email", validators=[DataRequired("Email cannot be blank.")])
    password = PasswordField("Password")
    verified = SelectField(
        "Verified",
        choices=[(False, "False"), (True, "True")],
        validators=[DataRequired(message="Verification status is required.")],
    )
    roles = StringField("Roles")

    def validate_email(self, email):
        user = db.Users.find_one(
            {"_id": {"$ne": self.user_id.data}, "email": email.data}
        )
        if user:
            raise ValidationError("This email is already is use.")
