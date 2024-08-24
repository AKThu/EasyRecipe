import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv


UPLOAD_FOLDER = './static/images/'
DEFAULT_USER_PROFILE = '/images/anonymous.jpg'

app = Flask(__name__, static_folder='./static')
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///demo.db"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

db.init_app(app)