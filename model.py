from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column
from config import db


class User(db.Model):
    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(150), unique=True, nullable=False)
    password = mapped_column(String(300), nullable=False)