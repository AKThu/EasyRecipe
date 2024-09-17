# Easy Recipes
#### Video Demo: https://youtu.be/z5ijRYbaA2Q
#### Description: 

Easy Recipe is a website for sharing recipes. Users can create their accounts, explore recipes created by other users, and create recipes.

Techstack used for this project is Flask for the backend, jinja for templating, tailwind and daisyUI components for design, and SQLite for the database.

The project is created in a Python virtual environment (venv) so that different packages and specific versions of packages used by the project can be installed without breaking other projects.

## Files

### Frontend

Frontend template files are located in the project templates directory.

The "template.html" file is used as a base template for the basic layout of the website. It handles displaying the top navigation bar, search bar which is a modal, toast notifications for great feedback to the user, and a footer. Because it is a template file, it also contains a placeholder to display contents from other template files.

The "home.html" file is to display the home page of the website which contains the hero section, a list of recently added recipes, and top-rated recipes. Instead of directly putting the codes of these three different parts of the home page, three different HTML files are created, "hero-section.html", "newly_added_recipes.html" and "top_rated_recipes.html", which are inside the "home" directory, and then included inside the "home.html".

In the recipe directory, the "all_recipes.html" and "recipe_detail.html" files are located. The "all_recipes.html" file is responsible for displaying a list of all recipes, 20 recipes at a time with pagination. The "recipe_detail.html" file is responsible for displaying details of the recipe, cook duration, serving amount, average rating, ingredients of the recipes, and step-by-step instructions on how to make the recipe. It also has a place for the user to give a rating to the current recipe.

The recipes on the website are user-uploaded, so there is a place for users to upload their recipes. "upload.html" is responsible for displaying a form for uploading recipes. Users can upload custom images for the recipe, cook duration, serving amount, ingredients, and step-by-step instructions.

In the "authentication" directory, the "login.html" and "register.html" files are responsible for displaying the user registration form and user login form. Username, email, and password fields are required for user registration. Once registered, the user can log in using email and password. Users can log out by the logout button in the dropdown menu, which is accessible by clicking the user icon in the navigation bar.

The "profile.html" file is responsible for displaying user info, changing profile images, and resetting passwords.

The "error.html" file is for displaying a custom page for HTTP errors.

### static files

Static files like CSS files, javascript files, icons, and images are stored in the static directory.

### Backend

For handling the backend 4 different python files are used.

- "app.py" is the main file and it includes different routes to handle different HTTP requests and to return appropriate responses to the frontend.
- "config.py" for configuring the flask app with an upload folder path to store user-uploaded contents like user profile images and recipe images and for configuring the data model and database URL to store user data, recipe data, and recipe ratings.
- "model.py" for creating database models.
- "helpers.py" for creating helper functions to abstract the logic and remove repetitive code blocks in the main file.

#### In "app.py"

- ```register```, ```login``` and ```logout``` functions handle the authentication.
- ```home``` function for querying recently added recipes and top-rated recipes, and include them in the response.
- ```profile``` function for querying username, email, and user profile, and include them in the response.
- ```change_profile_image``` function handles the uploading of the user profile image.
- ```recipes``` function queries 20 recipes per page from the database and includes them in the response.
- ```recipe_detail``` function queries the recipe name, recipe image, cook duration, serving amount, ingredients, step-by-step instructions, average rating, and the rating given by the current user, and includes them in the response.
- ```upload``` function handles the uploading of a new recipe.
- ```rate_recipe``` function handles giving the rating and updating the rating of the recipe.
- ```page_not_found``` function handles the error handling and responding with the corresponding error page.
Except for register and login, every other route is protected with the @login_required wrapper function which is defined inside of "helper.py".

### Database

SQLite is used for the database and it is managed by using the flask-sqlalchemy python package. Defining the database models are located inside "model.py". The SQLite database includes three database tables, "user", "recipe" and "rating" tables.

The "user" table is for storing user data and it has the primary key column "id", username column, email column, password column, and profile_image column. The user profile image is stored in the file system and its path is stored in the profile_image column of the database.

The "recipe" table stores the recipe data and it has the primary key column "id", foreign key column "user_id" which references the "id" column in the "user" table, name column, cook_time_in_minutes column, servings column, ingredients column which store each ingredient as JSON, instructions column which stores each step as JSON, image column to store the URL of the recipe stored in the file system, datatime column to store uploaded date and time, average_rating column and total_rating column.

The "rating" table stores the rating given by each user to each recipe and it has the primary key column "id", the foreign key column "recipe_id" which references the "id" column in the "recipe" table, another foreign key column "user_id" which references to the "id" column in "user" table and rating column.

