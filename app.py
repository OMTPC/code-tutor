from flask import Flask, render_template
import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "CodeTutor_Project"

@app.route("/")
def home():
    #current_year = datetime.datetime.now().year
    return render_template("Homepage.html")

if __name__ == "__main__":
    app.run(debug=True)


