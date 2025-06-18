from cryptography.fernet import Fernet
import base64
import hashlib

def generate_key(password: bytes) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(password).digest())

def encrypt_data(data: str, password: bytes) -> bytes:
    key = generate_key(password)
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, password: bytes) -> str:
    key = generate_key(password)
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()
