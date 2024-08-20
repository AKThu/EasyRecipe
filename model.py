from sqlalchemy import Integer, String, JSON, ForeignKey
from sqlalchemy.orm import mapped_column
from config import db


class User(db.Model):
    __tablename__ = "user"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(150), unique=True, nullable=False)
    password = mapped_column(String(300), nullable=False)

class Recipe(db.Model):
    __tablename__ = "recipe"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(200), nullable=False)
    cook_time_in_minutes = mapped_column(Integer, nullable=False)
    servings = mapped_column(Integer, nullable=False)
    ingredients = mapped_column(JSON, nullable=False)
    instructions = mapped_column(JSON, nullable=False)
    image = mapped_column(String(255), nullable=False)
    datetime = mapped_column(String(100), nullable=False)
    user_id = mapped_column(Integer, ForeignKey("user.id"))