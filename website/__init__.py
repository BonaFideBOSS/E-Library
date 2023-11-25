# Import modules
from flask import Flask
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

app = Flask(__name__, template_folder="views", static_folder="assets")
db = PyMongo()
csrf = CSRFProtect()
mail = Mail()


def flask_app():
    app.config.from_pyfile("../config.py")

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