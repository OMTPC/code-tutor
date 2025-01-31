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

    module_progress = db.relationship('UserModuleProgress', backref='user', lazy=True)
    exercise_progress = db.relationship('UserExerciseProgress', backref='user', lazy=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        # Return the unique identifier for the user (typically the "userid")
        return str(self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    

# Module Table
class Module(db.Model):
    moduleid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('locked', 'available', 'completed', name='module_status'), default='locked')
    
    # Relationships
    exercises = db.relationship('Exercise', backref='module', lazy=True)
    user_progress = db.relationship('UserModuleProgress', backref='module', lazy=True)

    def __repr__(self):
        return f"Module('{self.title}', '{self.status}')"
    
# Exercise Table
class Exercise(db.Model):
    exerciseid = db.Column(db.Integer, primary_key=True)
    moduleid = db.Column(db.Integer, db.ForeignKey('module.moduleid'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('locked', 'available', 'completed', name='exercise_status'), default='locked')
    

    # Relationships
    user_progress = db.relationship('UserExerciseProgress', backref='exercise', lazy=True)

    def __repr__(self):
        return f"Exercise('{self.title}', '{self.status}')"
    

# User Module Progress
class UserModuleProgress(db.Model):
    UMPid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    moduleid = db.Column(db.Integer, db.ForeignKey('module.moduleid'), nullable=False)
    status = db.Column(db.Enum('locked', 'available', 'completed', name='progress_status'), default='locked')
    progress = db.Column(db.Integer, default=0)  # Progress in percentage (0-100)
    
    
    def __repr__(self):
        return f"UserModuleProgress(User ID: {self.userid}, Module ID: {self.moduleid}, Status: {self.status})"
# User Exercise Progress
class UserExerciseProgress(db.Model):
    UEPid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=False)
    status = db.Column(db.Enum('locked', 'available', 'completed', name='exercise_progress_status'), default='locked')
    

    def __repr__(self):
        return f"UserExerciseProgress(User ID: {self.userid}, Exercise ID: {self.exerciseid}, Status: {self.status})"


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

            # Create UserModuleProgress for all modules if not present
            modules = Module.query.all()
            for module in modules:
                user_module_progress = UserModuleProgress.query.filter_by(userid=user.userid, moduleid=module.moduleid).first()
                if not user_module_progress:
                    new_progress = UserModuleProgress(userid=user.userid, moduleid=module.moduleid, status='locked')
                    db.session.add(new_progress)

            # Unlock only the first module (moduleid=1)
            first_module = Module.query.filter_by(moduleid=1).first()  # Assuming the first module has moduleid=1
            user_module_progress = UserModuleProgress.query.filter_by(userid=user.userid, moduleid=first_module.moduleid).first()

            if user_module_progress and user_module_progress.status == 'locked':
                user_module_progress.status = 'available'
                db.session.commit()  # Commit the changes to the database

            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")  # Redirect to the intended page
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)




@app.route("/dashboard")
@login_required  # Ensures the user is logged in before accessing the dashboard
def dashboard():
    # Get the user's progress for each module
    user_modules = []
    modules = Module.query.all()  # Get all modules

    for module in modules:
        user_module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module.moduleid).first()
        if user_module_progress:
            user_modules.append({
                'module': module,
                'status': user_module_progress.status,
                'progress': user_module_progress.progress
            })
        else:
            user_modules.append({
                'module': module,
                'status': 'locked',
                'progress': 0
            })

    return render_template("dashboard.html", username=current_user.username, user_modules=user_modules)


@app.route("/module/<int:module_id>/exercises")
@login_required
def exercises(module_id):
    # Fetch the module from the database
    module = Module.query.get_or_404(module_id)

    # Fetch the exercises associated with the module
    exercises = Exercise.query.filter_by(moduleid=module_id).all()

    # Get the user's progress for this module
    user_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()

    # If user has not started the module, set the progress to 'locked'
    if not user_progress:
        user_progress = UserModuleProgress(userid=current_user.userid, moduleid=module_id, status='locked', progress=0)
        db.session.add(user_progress)
        db.session.commit()

    return render_template("exercise.html", module=module, exercises=exercises, user_progress=user_progress)




@app.route("/logout")
@login_required  # Ensure the user is logged in before logging out
def logout():
    logout_user()  # Logs out the current user
    flash("You have been logged out.", "success")  # Optionally, flash a message
    return redirect(url_for("home"))  # Redirect to the home page or login page



if __name__ == "__main__":
    app.run(debug=True)


