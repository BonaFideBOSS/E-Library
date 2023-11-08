from flask import Flask
from flask_pymongo import PyMongo
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

db = PyMongo()
csrf = CSRFProtect()
mail = Mail()


def flask_app():
    app = Flask(__name__, template_folder="views", static_folder="assets")
    app.config.from_pyfile("../config.py")

    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app
