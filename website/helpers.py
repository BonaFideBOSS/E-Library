from . import app
import hashlib
import string
import secrets
import requests
import base64
import io
from flask_wtf.file import FileStorage
from filestack import Client, Filelink


# Function to form a search query to pass to the database to filter records
def db_searcher(fields: list[str], string: str):
    query = {"$or": []}
    for field in fields:
        query["$or"].append(
            {"$and": [{field: {"$regex": i, "$options": "i"}} for i in string.split()]}
        )
    return query


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


# Function to upload an image file to cloud
def upload_image_to_cloud(image: FileStorage, name: str):
    image_url = None
    try:
        API_KEY = app.config["IMGBB_API"]
        URL = "https://api.imgbb.com/1/upload"
        image = base64.b64encode(image.read())
        data = {"key": API_KEY, "image": image, "name": name}
        response = requests.post(URL, data).json()
        image_url = response["data"]["url"]
    except:
        pass
    return image_url


# Function to store a PDF file to cloud
def upload_pdf_to_cloud(pdf: FileStorage):
    pdf_url = None
    try:
        API_KEY = app.config["FILESTACK_API"]
        client = Client(API_KEY)
        response = client.upload(file_obj=io.BytesIO(pdf.read()))
        pdf_url = response.url
        print(pdf_url)
    except Exception as e:
        print(f"Error: {e}")
        pass
    return pdf_url


def get_file(url: str):
    file = Filelink(url.split("/")[-1])
    file = file.get_content()
    file = io.BytesIO(file)
    return file
