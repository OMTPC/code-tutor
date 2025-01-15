from flask import Flask, render_template, redirect, url_for, flash, request
from forms import LoginForm, RegisterForm
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codetutorDB.db'  # This will create a file with your Db name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To disable a feature we don't need

db = SQLAlchemy(app)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)  # Store hashed password
    registered_at = db.Column(db.DateTime, default=datetime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year = current_year)


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


