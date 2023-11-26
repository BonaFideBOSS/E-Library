# Import modules
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

db = db.db  # Get database
# Set default configuration
# Max file size limit
max_file_size = 20  # in MB
# Types of supported files
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
# Common file validators
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


# Category Form - Used to validate and render category form
# Used when editing a category
class CategoryForm(FlaskForm):
    # Category Id
    category_id = StringField("Category Id", render_kw={"disabled": True})
    # Category name
    category = StringField(
        "Category", validators=[DataRequired("Category title is required.")]
    )
    # Category icon
    icon = StringField("Icon", validators=[DataRequired("Icon is required.")])
    # Category image - an image acting as background image
    # Not required when editing
    image = FileField("Image", validators=file_validators)
    # Edit button
    submit = SubmitField("Save Changes")

    # Function to check whether category with the same name already exist
    def validate_category(self, category):
        query = {"category": category.data}
        query["_id"] = {"$ne": self.category_id.data}
        category = db.Categories.find_one(query)
        if category:
            raise ValidationError("This category is already defined.")


# Category Form - Used when creating a new category
# Same structure as the main category form
class NewCategoryForm(CategoryForm):
    # Hides the category Id field
    category_id = HiddenField()
    # Category image is required
    image = FileField(
        "Image", validators=[FileRequired("An image is required.")] + file_validators
    )
    # Add button
    submit = SubmitField("Add New Category")


# Books Form - Used to validate books and videos when updating them
class BooksForm(FlaskForm):
    # Book Id
    book_id = StringField("Book Id", render_kw={"disabled": True})
    # Type of content - Book or Video
    type = SelectField(
        "Type",
        choices=[("book", "Book"), ("video", "Video")],
        validators=[DataRequired(message="Material type is required.")],
    )
    # Category Id
    category_id = SelectField(
        "Category",
        validators=[DataRequired("Category is required.")],
    )
    # Title of the book or Video
    title = StringField("Title", validators=[DataRequired("Title is required.")])
    # Publish year of the book or video
    year = IntegerField(
        "Publish Year",
        validators=[
            DataRequired("Year is required."),
            NumberRange(
                min=1000,
                # Cannot be greater than current year
                max=datetime.now().year,
                message="Year cannot be greater than current year.",
            ),
        ],
    )
    # Author name
    author = StringField(
        "Author(s) (split by comma if more than one)",
        validators=[DataRequired("Author is required.")],
    )
    # Publisher name
    publisher = StringField(
        "Publisher", validators=[DataRequired("Publisher is required.")]
    )
    # Book/Video summary or description
    summary = TextAreaField(
        "Summary",
        validators=[
            DataRequired("Summary is required."),
            Length(
                # Maximum of 1000 characters
                min=10,
                max=1000,
                message="Summary must be 10 to 1000 characters long.",
            ),
        ],
    )
    # Book cover or video thumbnail
    cover = FileField("Cover", validators=file_validators)
    # Book - PDF format
    book = FileField("Book (PDF)", validators=file_validators)
    # Video - URL string
    video = StringField("Video (YouTube Embed URL)")
    # Downloadable - True or False
    downloadable = SelectField(
        "Downloadable",
        choices=[(False, "False"), (True, "True")],
        validators=[DataRequired(message="Downloadable status is required.")],
    )
    # Submit button
    submit = SubmitField("Save Changes")

    # Function to show a list of categories
    def is_submitted(self):
        self.category_id.choices = [
            (c["_id"], c["category"]) for c in db.Categories.find({})
        ]
        return super().is_submitted()


# New Book/Video Form - Inheritance the main BookForm Class
class NewBookForm(BooksForm):
    # Book Id is hidden
    # Book Id is automatically generated
    book_id = HiddenField()
    # Cover/thumbnail is required
    cover = FileField(
        "Cover", validators=[FileRequired("Cover is required.")] + file_validators
    )
    # Add button
    submit = SubmitField("Add New Book")

    # Function to validate details
    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        # Throws an error if type of content is "book" and book is not given
        if self.type.data == "book" and self.book.data == None:
            self.book.errors.append("Book is required.")
            return False

        # Throws an error if type of content is "video" and video is not given
        if self.type.data == "video" and self.video.data == "":
            self.video.errors.append("Video is required.")
            return False

        return True


# User Form - Used to validate user details
class UserForm(FlaskForm):
    # User Id
    user_id = StringField("User Id", render_kw={"disabled": True})
    # User avatar
    avatar = StringField("Avatar", validators=[DataRequired("Avatar is required.")])
    # Username field
    username = StringField(
        "Username", validators=[DataRequired("Username cannot be blank.")]
    )
    # Email field
    email = EmailField("Email", validators=[DataRequired("Email cannot be blank.")])
    # Password field
    password = PasswordField("Password")
    # Verified field - True or False
    verified = SelectField(
        "Verified",
        choices=[(False, "False"), (True, "True")],
        validators=[DataRequired(message="Verification status is required.")],
    )
    # User roles
    roles = StringField("Roles")

    # Function to validate if email is unique
    def validate_email(self, email):
        user = db.Users.find_one(
            {"_id": {"$ne": self.user_id.data}, "email": email.data}
        )
        if user:
            raise ValidationError("This email is already is use.")
