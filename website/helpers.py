import hashlib
import string
import secrets


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
