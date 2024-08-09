from flask import render_template, redirect, request, flash, session
from config import app, db
from model import User, Recipe
from http import HTTPStatus
from helpers import error, password_hash, check_password


@app.route("/")
def home():
    # TODO
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
            return render_template("error.html", error=error(HTTPStatus.FORBIDDEN, "Please enter value in all input fields"))

        # check password confirmation
        if password != repassword:
            return render_template("error.html", error=error(HTTPStatus.IM_A_TEAPOT, "Two passwords do not match"))

        # check if the user with the same email already exists
        user_exists = bool(db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none())
        if user_exists:
            return render_template("error.html", error=error(HTTPStatus.FORBIDDEN, "The email is already registered"))

        # create user object
        user = User(
            username = username,
            email = email,
            password = password_hash(password)
        )
        
        # register the user
        db.session.add(user)
        db.session.commit()

        # refresh the user data after inserting to the database to be able to access the "id"
        db.session.refresh(user)
        # set session data
        session["user_id"] = user.id

        # redirect user to the home page
        flash("Registered successfully!", "success")
        return redirect("/")

    # if user reached the route via GET method
    else:
        return render_template("authentication/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # if user is submitting(POST) the login form
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        # check if input fields contain values
        if not email or not password:
            return render_template("error.html", error=error(HTTPStatus.FORBIDDEN, "Please enter value in all input fields"))
        
        # check if user exists
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if not user:
            return render_template("error.html", error=error(HTTPStatus.NOT_FOUND, "User does not exists!"))
        
        # check password
        if not check_password(user, password):
            return render_template("error.html", error=error(HTTPStatus.UNAUTHORIZED, "Wrong Password"))
        
        # set session data
        session["user_id"] = user.id

        # redirect user to the home page
        flash("Login successful", "success")
        return redirect("/")

    # if user reached the route via GET method
    else:
        return render_template("authentication/login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect("/")


@app.route("/recipes")
def recipes():
    return render_template("/recipe/all_recipes.html")


@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id):

    # Query recipe from database
    recipe = db.session.execute(db.select(Recipe).filter_by(id=recipe_id)).scalar_one_or_none()

    # If recipe is not found
    if not recipe:
        return render_template("error.html", error=error(HTTPStatus.NOT_FOUND, "Not Found"))
    
    if recipe.cook_time_in_minutes >= 60:
        recipe.cook_time_hour = recipe.cook_time_in_minutes // 60
        recipe.cook_time_minute = recipe.cook_time_in_minutes % 60
    else:
        recipe.cook_time_hour = None
        recipe.cook_time_minute = recipe.cook_time_in_minutes
    
    print(type(recipe))
    
    return render_template("/recipe/recipe_detail.html", recipe=recipe)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)