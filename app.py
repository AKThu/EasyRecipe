import os

from flask import render_template, redirect, request, flash, session
from config import app, db, DEFAULT_USER_PROFILE
from model import User, Recipe, Rating
from http import HTTPStatus
from helpers import error, password_hash, check_password, allowed_file, get_current_time, string_to_datetime, login_required, generate_profile_name, get_avg_rating
from werkzeug.utils import secure_filename
from sqlalchemy import desc


@app.route("/")
@login_required
def home():
    # newly added recipes
    new_recipes = db.session.execute(db.select(Recipe).order_by(desc(Recipe.id))).scalars().fetchmany(4)

    # top rated recipes
    top_rated_recipes = db.session.execute(db.select(Recipe).order_by())

    users = db.session.execute(db.select(User).order_by(User.username)).scalars().fetchall()
    return render_template("home.html", new_recipes=new_recipes, users=users)


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
            password = password_hash(password),
        )
        
        # register the user
        db.session.add(user)
        db.session.commit()

        # refresh the user data after inserting to the database to be able to access the "id"
        db.session.refresh(user)
        # set session data
        session["user_id"] = user.id
        session["username"] = username
        session["user_profile_image"] = DEFAULT_USER_PROFILE

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
            flash("Input fields required.", "error")
            return redirect(request.url)
        
        # check if user exists
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if not user:
            flash("User does not exists.", "error")
            return redirect(request.url)
        
        # check password
        if not check_password(user, password):
            flash("Wrong password", "error")
            return redirect(request.url)
        
        # set session data
        session["user_id"] = user.id
        session["username"] = user.username
        session["user_profile_image"] = user.profile_image

        # redirect user to the home page
        flash("Login successful", "success")
        return redirect("/")

    # if user reached the route via GET method
    else:
        return render_template("authentication/login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        # Get old password and new password from post request
        old_password = request.form.get("old_password").strip()
        new_password = request.form.get("new_password").strip()

        # Check if two password fields exists
        if not old_password or not new_password:
            flash("Missing input!", "error")
            return redirect(request.url)

        # Get user from the database and check if the old password is correct
        user = db.session.execute(db.select(User).filter_by(id=session["user_id"])).scalar_one_or_none()
        if not check_password(user, old_password):
            flash("Wrong password", "error")
            return redirect(request.url)
        
        # Update the password
        user.password = password_hash(new_password)
        db.session.commit()
        
        # Redirect user to profile page
        flash("Profile updated!", "success")
        return redirect(request.url)
    else:
        email = db.session.execute(db.select(User.email).filter_by(id=session["user_id"])).scalar_one_or_none()
        return render_template("profile.html", email=email)


@app.route("/change_profile_image", methods=["POST"])
@login_required
def change_profile_image():
    # Validate if profile_image part is included in the request header
    if 'profile_image' not in request.files:
        flash('No image part')
        return redirect(request.url)
    profile_image = request.files['profile_image']
    if profile_image == '':
        flash('Image not selected')
        return redirect(request.url)
    
    # Save image to the file system
    save_location = ''
    if profile_image and allowed_file(profile_image.filename):
        filename = generate_profile_name(profile_image.filename)
        save_location = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        profile_image.save(save_location)
    else:
        flash("Invalid file extension. (only '.png', '.jpg' or '.jpeg' files are allowed)", "error")
    
    # Get user from the database table
    user = db.session.execute(db.select(User).filter_by(id=session["user_id"])).scalar_one_or_none()
    # Delete old profile image
    if not user.profile_image == DEFAULT_USER_PROFILE:
        os.remove('./static/'+user.profile_image)
    # Update profile image
    user.profile_image = save_location.split('/', 2)[2]
    db.session.commit()

    # change profile image in the session data
    session['user_profile_image'] = user.profile_image

    # Redirect user to profile page
    flash("Profile updated successfully", "success")
    return redirect("/profile")


@app.route("/recipes")
@login_required
def recipes():
    recipes = db.paginate(db.select(Recipe).order_by(Recipe.id), page=int(request.args.get("page", "1")))
    return render_template("/recipe/all_recipes.html", recipes=recipes)


@app.route("/recipe/<recipe_id>")
@login_required
def recipe_detail(recipe_id):
    # Query recipe from database
    recipe = db.session.execute(db.select(Recipe).filter_by(id=recipe_id)).scalar_one_or_none()
    
    # If recipe is not found
    if not recipe:
        return render_template("error.html", error=error(HTTPStatus.NOT_FOUND))
    
    # Covert cooking time from minutes to hour and minutes
    if recipe.cook_time_in_minutes >= 60:
        recipe.cook_time_hour = recipe.cook_time_in_minutes // 60
        recipe.cook_time_minute = recipe.cook_time_in_minutes % 60
    else:
        recipe.cook_time_hour = None
        recipe.cook_time_minute = recipe.cook_time_in_minutes

    # Get the rating of current user
    current_user_rating = db.session.execute(db.select(Rating).filter_by(recipe_id=recipe_id, user_id=session["user_id"])).scalar_one_or_none()
    current_user_rating = current_user_rating.rating if current_user_rating else 0
        
    return render_template("/recipe/recipe_detail.html", recipe=recipe, current_user_rating=current_user_rating)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # handle image upload
        if 'image' not in request.files:
            flash('No image part')
            return redirect(request.url)
        image = request.files['image']
        if image.filename == '':
            flash('Image not selected')
            return redirect(request.url)
        
        # handle recipe name
        if request.form["name"] == "":
            flash("Required recipe name")
            return redirect(request.url)
        
        # handle cooking duration
        if (request.form["hours"] == "") or (request.form["minutes"] == "") or (request.form["hours"] == "0" and request.form["minutes"] == "0"):
            flash("Required cooking duration")
            return redirect(request.url)
        
        # handle servings
        if request.form["servings"] == "" or request.form["servings"] == "0":
            flash("Required servings amount")
            return redirect(request.url)
        
        # handle ingredients
        if request.form["ingredients"] == "":
            flash("Required a list of ingredients")
            return redirect(request.url)

        # handle cooking instruction steps
        if request.form["step"] == "":
            flash("Required instructions to cook")
            return redirect(request.url)

        # save image to the storage
        save_location = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            save_location = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(save_location)
        else:
            flash("Invalid file extension. (only '.png', '.jpg' or '.jpeg' files are allowed)", "error")
            return redirect(request.url)

        # create Recipe object
        recipe = Recipe(
            name = request.form.get("name"),
            cook_time_in_minutes = (int(request.form["hours"]) * 60) + int(request.form["minutes"]),
            servings = request.form.get("servings"),
            ingredients = request.form["ingredients"].split("\r\n"),
            instructions = request.form.getlist("step"),
            image = save_location.split('/', 2)[2],
            datetime = get_current_time(),
            user_id = session["user_id"]
        )

        db.session.add(recipe)
        db.session.commit()

        flash("New recipe added.", "success")
        return redirect("/")

    else:
        return render_template("/upload.html")
    

@app.route("/recipe/<int:recipe_id>/rate", methods=["POST"])
@login_required
def rate_recipe(recipe_id):
    ## Adding a new row or updating the rating table
    # add rating to database if not already exists otherwise update the already existing row
    rating = db.session.execute(db.select(Rating).filter_by(user_id=session["user_id"], recipe_id=recipe_id)).scalar_one_or_none()
    # if user already rated before the recipe
    if rating:
        rating.rating = request.form.get("rating")
    # if user has never been rated the recipe
    else:
        rating = Rating(
            recipe_id = recipe_id,
            user_id = session["user_id"],
            rating = request.form.get("rating")
        )
        db.session.add(rating)

    # Save changes to the database
    db.session.commit()

    ## Updating the average_rating column of recipe table
    # get all rating rows of current recipe
    ratings = db.session.execute(db.select(Rating).filter_by(recipe_id=recipe_id)).scalars().all()
    # get total ratings
    total_ratings = len(ratings)
    # calculate average rating
    average_rating = get_avg_rating(ratings)

    # get current recipe row to update total_ratings and average_rating column
    recipe = db.session.execute(db.select(Recipe).filter_by(id=recipe_id)).scalar_one_or_none()
    # update total_ratings and average_rating
    recipe.total_ratings = total_ratings
    recipe.average_rating = average_rating
    # save changes to database
    db.session.commit()
    
    flash("thank you for rating", "success")
    return redirect("/recipe/{recipe_id}".format(recipe_id=recipe_id))

# ERROR HANDLING
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error=error(HTTPStatus.NOT_FOUND))
    

# TEST ROUTE
@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        print(request.form.get("rating"))
        return render_template("test.html", data=request.form.get("rating"))
    else:
        return render_template("test.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)