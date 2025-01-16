from flask import Flask, render_template, redirect, url_for, flash, request
from forms import LoginForm, RegisterForm
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)

app.config["SECRET_KEY"] = "Catianair25"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codetutorDB.db"  # This will create a file with your Db name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To disable a feature we don"t need

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect unauthorized users to the login page
login_manager.login_message = "Please log in to access this page."

# Define the user_loader function that Flask-Login will use to load the user from the database
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))  # Retrieve the user based on their ID

class User(UserMixin,db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)  # Store hashed password
    registered_at = db.Column(db.DateTime, default=func.now)  

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # Return the unique identifier for the user (typically the "userid")
        return str(self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year = current_year)


#register route - to create a regioster page for user to register their details
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()  # Your form for registering users
    
    if form.validate_on_submit():
        # Check if the user already exists based on email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))
        
        # Hash the password using werkzeug.security
        hashed_password = generate_password_hash(form.password.data)

        # Create a new user instance with the form data
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            registered_at=func.now() # Automatically set registration time
        )

        try:
            db.session.add(new_user)  # Add the new user to the session
            db.session.commit()  # Commit the transaction to save the user
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))  # Redirect to login page after successful registration
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f"Error registering user: {e}", "danger")
    
    return render_template("register.html", form=form)  # Render the registration form



#login route - to login after register
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):  # Check password
            login_user(user, remember=form.remember.data)  # Log the user in
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")  # Redirect to the intended page
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required  # Ensures the user is logged in before accessing the dashboard
def dashboard():
    # Assuming you have a User model with a `username` attribute
    return render_template("dashboard.html", username=current_user.username)


@app.route("/logout")
@login_required  # Ensure the user is logged in before logging out
def logout():
    logout_user()  # Logs out the current user
    flash("You have been logged out.", "success")  # Optionally, flash a message
    return redirect(url_for("home"))  # Redirect to the home page or login page



if __name__ == "__main__":
    app.run(debug=True)


