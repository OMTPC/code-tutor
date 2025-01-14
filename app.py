from flask import Flask, render_template, redirect, url_for, flash, request
from forms import LoginForm, RegisterForm
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = "CodeTutor_Project"

# Set up the database URI (SQLite for development)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codementor.db'  # You can change this for other databases
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable tracking modifications to save memory

# Initialize the database instance
db = SQLAlchemy(app)



@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year = current_year)

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()  # This will create all tables defined in models


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login Successful!", "success")
        return redirect(url_for("home"))
    return render_template("login.html", form = form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("Registration Successful!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form = form)


if __name__ == "__main__":
    app.run(debug=True)


