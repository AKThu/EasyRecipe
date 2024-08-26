import datetime

from hashlib import sha256
from functools import wraps
from flask import session, redirect


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def error(http_status):
    return {
        "status_code": http_status.value,
        "phrase": http_status.phrase,
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

def generate_profile_name(filename):
    [name, extension] = filename.rsplit(".", 1)
    return "{name}_{date_time}.{extension}".format(name=name, date_time=datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S_%f"), extension=extension)

def get_avg_rating(ratings):
    total_rating = 0
    for rating in ratings:
        total_rating += rating.rating
    return round(total_rating / len(ratings), ndigits=1) if len(ratings) != 0 else 0