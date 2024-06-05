# Import modules
from flask import Flask
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
import os

app = Flask(__name__, template_folder="views", static_folder="assets")
db = PyMongo()
csrf = CSRFProtect()
mail = Mail()

try:
    app.config.from_pyfile("../config.py")
except:
    app.config["WEBSITE_INFO"] = {
        "name": "E-Library",
        "logo": '<i class="fa-sharp fa-solid fa-book-open-cover"></i>',
        "description": "Online Library Management System",
        "web_address": "elibrary.almir.info",
    }
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.config["IMGBB_API"] = os.environ.get("IMGBB_API")
    app.config["FILESTACK_API"] = os.environ.get("FILESTACK_API")
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
    app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
    app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL")
    app.config["MAIL_DEFAULT_SENDER"] = ("E-Library", "contact@almir.info")


def flask_app():
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin
    from .user import user

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(user, url_prefix="/user")

    return app
