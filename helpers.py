from hashlib import sha256

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