import datetime

from hashlib import sha256
from functools import wraps
from flask import session, redirect


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_time():
    return datetime.datetime.now().strftime("%x %X")

def string_to_datetime(datetime_string):
    return datetime.datetime.strptime(datetime_string, "%x %X")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

