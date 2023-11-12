from . import app
import hashlib
import string
import secrets
import requests
import base64
from flask_wtf.file import FileStorage


# Function to encrypt a message using MD5 Hash algorithm
def encrypt_message(message: str):
    encrypted_message = hashlib.md5(message.encode()).hexdigest()
    return encrypted_message


# Function to generate a random alphanumeric string
def generate_otp(count: int = 6):
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for _ in range(count))
    return password


# Function to generate a hard-to-guess URL-safe text string
def generate_token(count: int = 32):
    return secrets.token_urlsafe(count)


def upload_image_to_cloud(image: FileStorage, name: str):
    API_KEY = app.config["IMGBB_API"]
    URL = "https://api.imgbb.com/1/upload"
    image_url = None
    try:
        image = base64.b64encode(image.read())
        data = {"key": API_KEY, "image": image, "name": name}
        response = requests.post(URL, data).json()
        image_url = response["data"]["url"]
    except:
        pass
    return image_url
