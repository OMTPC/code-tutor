"""
Created by: Orlando Caetano
Date: [Insert Date]
Description: 
    This is a Flask-based web application for Code Tutor, designed to help novice programmers 
    learn Python through structured exercises and modules. [more to come]
Resources: [Please refer to resources.txt]
"""


from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from forms import LoginForm, RegisterForm
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import re

# Initialize Flask app
app = Flask(__name__)

# Secret key for security
app.config["SECRET_KEY"] = "Catianair25"

# Database configuration (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codetutorDB.db"  
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect unauthorized users to the login page
login_manager.login_message = "Please log in to access this page."

# Load user session from database
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))  

# database models
class User(UserMixin,db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)  # Store hashed password
    registered_at = db.Column(db.DateTime, default=func.now)  

    # Relationships with other tables
    module_progress = db.relationship('UserModuleProgress', backref='user', lazy=True)
    exercise_progress = db.relationship('UserExerciseProgress', backref='user', lazy=True)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Required method for Flask-Login
    def get_id(self):
        return str(self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    

# Module Table
class Module(db.Model):
    moduleid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('locked', 'available', 'completed', name='module_status'), default='locked')
    
    # Relationships with other tables
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
    
    status = db.Column(db.Enum('locked', 'available', 'completed', name='exercise_status'), default='locked')
    

    # Relationships with other tables
    user_progress = db.relationship('UserExerciseProgress', backref='exercise', lazy=True)

    def __repr__(self):
        return f"Exercise('{self.title}', '{self.status}')"


# Exercise solution Table
class Solution(db.Model):
    solutionid = db.Column(db.Integer, primary_key=True)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=False)
    solution_text = db.Column(db.Text, nullable=True)  # Solution as plain text
    solution_regex = db.Column(db.Text, nullable=True)  # Solution as regex pattern
    solution_type = db.Column(db.Enum('text', 'regex', name='solution_type'), nullable=False, default='text')  # Type of solution (text or regex)


    # Relationship back to Exercise
    exercise = db.relationship('Exercise', backref=db.backref('solutions', lazy=True))

    def __repr__(self):
        return f"Solution('{self.solution_text[:30]}...')"


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


#check user solution function
def check_solution(user_code, exercise_id):
    # Get the solution for the given exercise
    solutions = Solution.query.filter_by(exerciseid=exercise_id).all()

    # Check if any solution matches the user code
    for solution in solutions:
        if solution.solution_type == 'text' and solution.solution_text.strip().lower() == user_code.strip().lower():
            return "Correct!"  # User's code matches the exact text solution

        if solution.solution_type == 'regex':
            # Check if the user's code matches the regex pattern
            pattern = re.compile(solution.solution_regex)
            if pattern.match(user_code.strip()):
                return "Correct!"  # User's code matches the regex solution

    return "Incorrect. Please try again."  # If no solutions match

# Flask route to check the user's code (API)
@app.route('/check_code', methods=['POST'])
def check_code():
    data = request.get_json()

    if not data or 'code' not in data or 'exercise_id' not in data:
        return jsonify({'result': 'Error: Missing code or exercise ID'}), 400  # Bad Request

    user_code = data['code']
    exercise_id = data['exercise_id']

    result = check_solution(user_code, exercise_id)

    if result == "Correct!":
        # Update the progress for the exercise
        progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise_id).first()
        if not progress:
            progress = UserExerciseProgress(userid=current_user.userid, exerciseid=exercise_id, status='completed')
            db.session.add(progress)
        else:
            progress.status = 'completed'

        db.session.commit()

        # Check if the user has completed all exercises in the current module
        module_id = Exercise.query.filter_by(exerciseid=exercise_id).first().moduleid
        completed_exercises = UserExerciseProgress.query.filter_by(userid=current_user.userid, status='completed').join(Exercise).filter(Exercise.moduleid == module_id).count()

        total_exercises = Exercise.query.filter_by(moduleid=module_id).count()

        # If all exercises in the module are completed, mark the module as completed
        if completed_exercises == total_exercises:
            module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()
            if not module_progress:
                module_progress = UserModuleProgress(userid=current_user.userid, moduleid=module_id, status='completed')
                db.session.add(module_progress)
            else:
                module_progress.status = 'completed'

            db.session.commit()

    return jsonify({'result': result})




# Homepage route
@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year = current_year)


# Register route - allows users to create an account
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()  
    
    if form.validate_on_submit():
        # Check if the user already exists based on email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))
        
        # Hash the password 
        hashed_password = generate_password_hash(form.password.data)

        # Create a new user instance with the form data
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            registered_at=func.now() 
        )

        try:
            db.session.add(new_user)  
            db.session.commit()  
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))  
        except Exception as e:
            db.session.rollback() 
            flash(f"Error registering user: {e}", "danger")
    
    return render_template("register.html", form=form)  



# Login route - allows users to log in
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):  
            login_user(user, remember=form.remember.data)  

            # Initialize module progress for new users
            modules = Module.query.all()
            for module in modules:
                user_module_progress = UserModuleProgress.query.filter_by(userid=user.userid, moduleid=module.moduleid).first()
                if not user_module_progress:
                    new_progress = UserModuleProgress(userid=user.userid, moduleid=module.moduleid, status='locked')
                    db.session.add(new_progress)

            # Unlock only the first module (moduleid=1)
            first_module = Module.query.filter_by(moduleid=1).first()  
            user_module_progress = UserModuleProgress.query.filter_by(userid=user.userid, moduleid=first_module.moduleid).first()

            if user_module_progress and user_module_progress.status == 'locked':
                user_module_progress.status = 'available'
                db.session.commit()  

            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")  
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)



@app.route("/dashboard")
@login_required
def dashboard():
    # Initialize the list to store user modules and progress
    user_modules = []

    # Get all modules the user has access to
    modules = Module.query.all()

    for module in modules:
        user_module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module.moduleid).first()
        
        if user_module_progress:
            # Get all exercises for the module
            exercises = Exercise.query.filter_by(moduleid=module.moduleid).all()

            # Calculate progress (number of completed exercises / total exercises)
            completed_exercises = 0
            for exercise in exercises:
                user_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
                if user_exercise_progress and user_exercise_progress.status == 'completed':
                    completed_exercises += 1

            # Calculate percentage progress
            progress = int((completed_exercises / len(exercises)) * 100) if exercises else 0

            # Determine module status
            if module.moduleid > 1:  # The second module and beyond
                previous_module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module.moduleid - 1).first()
                if previous_module_progress and previous_module_progress.status == 'completed':
                    module_status = 'available'  # Next module becomes available after completing the previous one
                else:
                    module_status = 'locked'  # If previous module is not completed, lock the current module
            else:
                module_status = user_module_progress.status  # For the first module, use the user's current status

            # Add module progress and status to the list
            user_modules.append({
                'module': module,
                'status': module_status,
                'progress': progress
            })
        else:
            # If the user has no progress for this module, consider it locked
            user_modules.append({
                'module': module,
                'status': 'locked',
                'progress': 0
            })

    return render_template("dashboard.html", user_modules=user_modules)


@app.route("/module/<int:module_id>/exercises", methods=["GET", "POST"])
@login_required
def exercises(module_id):
    # Store module ID in the session to use in future routes
    session['current_module_id'] = module_id

    # Retrieve the module and its exercises
    module = Module.query.get_or_404(module_id)
    exercises = Exercise.query.filter_by(moduleid=module_id).order_by(Exercise.exerciseid).all()

    # Get user's progress for this module
    user_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()

    if not user_progress:
        # Create a new progress entry if none exists
        user_progress = UserModuleProgress(userid=current_user.userid, moduleid=module_id, status='available', progress=0)
        db.session.add(user_progress)
        db.session.commit()

    # Check exercise status and update the second one to 'available' if the first is completed
    for i, exercise in enumerate(exercises):
        user_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
        if not user_exercise_progress:
            status = 'available' if i == 0 else 'locked'  # The first exercise is available by default, the rest are locked
            user_exercise_progress = UserExerciseProgress(userid=current_user.userid, exerciseid=exercise.exerciseid, status=status)
            db.session.add(user_exercise_progress)
            db.session.commit()

    # Fetch updated progress for exercises
    exercise_progress = [
        UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
        for exercise in exercises
    ]

    # Handle exercise completion via POST request (when user finishes the exercise)
    if request.method == 'POST':
        completed_exercise_id = request.form.get('completed_exercise_id')
        if completed_exercise_id:
            # Mark the current exercise as completed
            completed_exercise = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=completed_exercise_id).first()
            if completed_exercise:
                completed_exercise.status = 'completed'  # Mark as completed
                db.session.commit()

                # Find the current exercise index
                current_exercise_index = next(i for i, exercise in enumerate(exercises) if str(exercise.exerciseid) == completed_exercise_id)

                # Unlock the next exercise
                next_exercise = exercises[current_exercise_index + 1] if current_exercise_index + 1 < len(exercises) else None
                if next_exercise:
                    next_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=next_exercise.exerciseid).first()
                    if next_exercise_progress:
                        next_exercise_progress.status = 'available'
                        db.session.commit()

                # Update module progress
                user_progress.progress = (user_progress.progress + 1) / len(exercises) * 100
                db.session.commit()

                # If the second exercise is completed, unlock the next module
                if completed_exercise_id == str(exercises[-1].exerciseid):  # If it's the second exercise
                    next_module = Module.query.filter(Module.moduleid > module_id).first()
                    if next_module:
                        # Unlock the second module for the user
                        user_module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=next_module.moduleid).first()
                        if not user_module_progress:
                            user_module_progress = UserModuleProgress(userid=current_user.userid, moduleid=next_module.moduleid, status='available', progress=0)
                            db.session.add(user_module_progress)
                            db.session.commit()

                        # Update the status of the module (unlocking the next module)
                        update_module_status(next_module.moduleid)  # Call this function to update the next module's status

                # Redirect to Future You page
                return redirect(url_for('future_you'))

    return render_template("exercise.html", module=module, exercises=exercises, exercise_progress=exercise_progress)


# Add this function to check and update the module status
def update_module_status(module_id):
    exercises = Exercise.query.filter_by(moduleid=module_id).all()
    completed_exercises = UserExerciseProgress.query.filter_by(userid=current_user.userid, status='completed').join(Exercise).filter(Exercise.moduleid == module_id).count()

    # If all exercises are completed, update module status to 'completed'
    if len(exercises) == completed_exercises:
        module_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()
        if module_progress:
            # Ensure the module stays completed or available for the user
            if module_progress.status != 'completed':
                module_progress.status = 'completed'
                db.session.commit()




@app.route("/future_you", methods=["GET", "POST"])
@login_required
def future_you():
    # Retrieve the current module ID from the session
    module_id = session.get('current_module_id')

    # Get the second exercise for the current module (explicitly)
    second_exercise = Exercise.query.filter_by(moduleid=module_id).order_by(Exercise.exerciseid).offset(1).first()  # Get the second exercise
    second_exercise_completed = UserExerciseProgress.query.filter_by(
        userid=current_user.userid,
        exerciseid=second_exercise.exerciseid,
        status='completed'
    ).first()

    print(f"Second Exercise Completed: {second_exercise_completed is not None}")

    if request.method == 'POST':
        if second_exercise_completed:
            # Find the next module based on the current module ID
            next_module = Module.query.filter(Module.moduleid > module_id).order_by(Module.moduleid.asc()).first()

            if next_module:
                # Get user progress for the next module
                user_module_progress = UserModuleProgress.query.filter_by(
                    userid=current_user.userid, 
                    moduleid=next_module.moduleid
                ).first()

                if user_module_progress:
                    print(f"Unlocking next module: {next_module.title}")

                    # Set the status of the next module to 'available'
                    user_module_progress.status = 'available'
                    user_module_progress.progress = 0  # Reset progress for the new module (optional)
                    db.session.commit()

                else:
                    print("User progress for the next module not found.")

            else:
                print("Next module not found.")

            # Redirect to the dashboard after completing the second exercise
            return redirect(url_for('dashboard'))  # Redirect to the dashboard

        else:
            # Redirect to the exercise page after completing the first exercise (if not completed the second one yet)
            return redirect(url_for('exercises', module_id=module_id))

    return render_template("future_you.html", second_exercise_completed=second_exercise_completed)





# Logout route
@app.route("/logout")
@login_required  # Ensure the user is logged in before logging out
def logout():
    logout_user()  # Logs out the current user
    flash("You have been logged out.", "success")  # Optionally, flash a message
    return redirect(url_for("home"))  # Redirect to the home page or login page



if __name__ == "__main__":
    app.run(debug=True)


