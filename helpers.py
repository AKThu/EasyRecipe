from hashlib import sha256
from os import getenv

def error(http_status, description):
    return {
        "status_code": http_status.value,
        "phrase": http_status,
        "description": description
    }

def password_hash(password):
    return sha256(password.encode('utf-8')).hexdigest()

def check_password(user, password):
    if user.password == password_hash(password):
        return True
    return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in getenv("ALLOWED_EXTENSIONS")