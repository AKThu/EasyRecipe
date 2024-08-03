from flask import render_template, redirect, request, flash
from config import app, db
from model import User
from hashlib import sha256
from http import HTTPStatus


@app.route("/")
def home():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars().fetchall()
    return render_template("home.html", users=users)


@app.route("/register", methods=["GET", "POST"])
def register():

    # if user is submitting(POST) a user registration form
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        repassword = request.form.get("repassword").strip()

        # check if input fields contain values
        if not username or not email or not password or not repassword:
            response = {
                "status_code": HTTPStatus.FORBIDDEN.value,
                "phrase": HTTPStatus.FORBIDDEN,
                "description": "Please enter value in all input fields"
            }
            return render_template("error.html", response=response)

        # check password confirmation
        if password != repassword:
            response = {
                "status_code": HTTPStatus.IM_A_TEAPOT.value,
                "phrase": HTTPStatus.IM_A_TEAPOT,
                "description": "Two passwords do not match",
            }
            return render_template("error.html", response=response)

        # check if the user with the same email already exists
        user_exists = bool(db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none())
        if user_exists:
            response = {
                "status_code": HTTPStatus.FORBIDDEN.value,
                "phrase": HTTPStatus.FORBIDDEN,
                "description": "The email is already registered",
            }
            return render_template("error.html", response=response )

        # create user object
        user = User(
            username = username,
            email = email,
            password = sha256(password.encode('utf-8')).hexdigest()
        )
        
        # register the user
        db.session.add(user)
        db.session.commit()

        # redirect user to the home page
        flash("Registered successfully!")
        return redirect("/")

    # if user reached the route via GET method
    else:
        return render_template("authentication/register.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)