from . import db
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SelectField,
    HiddenField,
    SubmitField,
    TextAreaField,
    IntegerField,
)
from flask_wtf.file import FileField, FileAllowed, FileSize, FileRequired
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange
from datetime import datetime

db = db.db
max_file_size = 20  # in MB
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


class BooksForm(FlaskForm):
    book_id = StringField("Book Id", render_kw={"disabled": True})
    type = SelectField(
        "Type",
        choices=[("book", "Book"), ("video", "Video")],
        validators=[DataRequired(message="Material type is required.")],
    )
    category_id = SelectField(
        "Category",
        choices=[(c["_id"], c["category"]) for c in db.Categories.find({})],
        validators=[DataRequired("Category is required.")],
    )
    title = StringField("Title", validators=[DataRequired("Title is required.")])
    year = IntegerField(
        "Publish Year",
        validators=[
            DataRequired("Year is required."),
            NumberRange(
                min=1000,
                max=datetime.now().year,
                message="Year cannot be greater than current year.",
            ),
        ],
    )
    author = StringField(
        "Author(s) (split by comma if more than one)",
        validators=[DataRequired("Author is required.")],
    )
    publisher = StringField(
        "Publisher", validators=[DataRequired("Publisher is required.")]
    )
    summary = TextAreaField(
        "Summary",
        validators=[
            DataRequired("Summary is required."),
            Length(
                min=10, max=1000, message="Summary must be 10 to 1000 characters long."
            ),
        ],
    )
    cover = FileField("Cover", validators=file_validators)
    book = FileField("Book (PDF)", validators=file_validators)
    video = StringField("Video (YouTube Embed URL)")
    downloadable = SelectField(
        "Downloadable",
        choices=[(False, "False"), (True, "True")],
        validators=[DataRequired(message="Downloadable status is required.")],
    )
    submit = SubmitField("Save Changes")


class NewBookForm(BooksForm):
    book_id = HiddenField()
    cover = FileField(
        "Cover", validators=[FileRequired("Cover is required.")] + file_validators
    )
    submit = SubmitField("Add New Book")

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        if self.type.data == "book" and self.book.data == None:
            self.book.errors.append("Book is required.")
            return False

        if self.type.data == "video" and self.video.data == "":
            self.video.errors.append("Video is required.")
            return False

        return True


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
