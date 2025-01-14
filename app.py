from flask import Flask, render_template, redirect, url_for, flash, request
from forms import LoginForm, RegisterForm
import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "CodeTutor_Project"

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


