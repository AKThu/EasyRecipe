from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

app = Flask(__name__)
app.secret_key = "testkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///demo.db"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

db.init_app(app)