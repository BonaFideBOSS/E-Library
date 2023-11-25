# Importing modules
from website import flask_app  # The web application
from flask import render_template
from flask_wtf.csrf import CSRFError

# Get the web application
app = flask_app()

# Run the web application
if __name__ == "__main__":
    app.run()


# Get the general information about the website before the application starts
@app.context_processor
def get_website_name():
    return dict(website_info=app.config["WEBSITE_INFO"])


# ===== Error Handling =====
@app.errorhandler(Exception)
def page_not_found(e):
    return render_template("404.html"), 404


# ===== CSRF Error Handling =====
@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return error.description, 400
