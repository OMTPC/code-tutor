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
    intro = db.Column(db.Text, nullable=True) 
    
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
    expected_output = db.Column(db.Text, nullable=True)  # Expected output for the solution

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

class CareerSuggestions(db.Model):
    CSid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=True)  # Link to Exercise table

    exercise = db.relationship('Exercise', backref='career_suggestions', lazy=True)  # Access career suggestions from exercise

    def __repr__(self):
        return f"<CareerSuggestion {self.title}>"

@app.route('/api/career_suggestions/<int:exerciseid>', methods=['GET'])
def get_career_suggestions(exerciseid):
    # Query career suggestions based on exerciseid
    career_suggestions = CareerSuggestions.query.filter_by(exerciseid=exerciseid).all()
    
    if career_suggestions:
        # Return the career suggestions in JSON format
        return jsonify([{
            "CSid": suggestion.id,
            "title": suggestion.title,
            "description": suggestion.description,
            
        } for suggestion in career_suggestions])
    else:
        return jsonify({"error": "No career suggestions found for this exercise"}), 404


# API Route to fetch an exercise
@app.route('/api/exercise/<int:exerciseid>', methods=['GET'])
def get_exercise(exerciseid):
    exercise = Exercise.query.get(exerciseid)
    if exercise:
        return jsonify({
            "exerciseid": exercise.exerciseid,
            "title": exercise.title,
            "description": exercise.description
        })
    return jsonify({"error": "Exercise not found"}), 404



#check user solution function
# Updated check_solution function to also make the next exercise available
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

        # Mark the next exercise as available
        next_exercise = Exercise.query.filter(Exercise.exerciseid > exercise_id, Exercise.moduleid == Exercise.query.filter_by(exerciseid=exercise_id).first().moduleid).order_by(Exercise.exerciseid).first()
        
        if next_exercise:
            next_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=next_exercise.exerciseid).first()
            if next_progress:
                next_progress.status = 'available'
            else:
                next_progress = UserExerciseProgress(userid=current_user.userid, exerciseid=next_exercise.exerciseid, status='available')
                db.session.add(next_progress)
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



@app.route('/module_intro/<int:module_id>', methods=['GET', 'POST'])
@login_required
def module_intro(module_id):
    # Get the module details from the database
    module = Module.query.get_or_404(module_id)
    
    # Get the user's progress in the module (to ensure they haven't already started)
    user_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()

    if request.method == 'POST':
        # If the user clicks to start the first exercise, redirect to exercises page
        return redirect(url_for('exercises', module_id=module_id))

    return render_template('module_intro.html', module=module)




@app.route("/module/<int:module_id>/exercises", methods=["GET", "POST"])
@login_required
def exercises(module_id):
    session['current_module_id'] = module_id

    # Retrieve the module and its exercises
    module = Module.query.get_or_404(module_id)
    exercises = Exercise.query.filter_by(moduleid=module_id).order_by(Exercise.exerciseid).all()

    # Ensure user progress exists for the module
    user_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()
    if not user_progress:
        user_progress = UserModuleProgress(userid=current_user.userid, moduleid=module_id, status='available', progress=0)
        db.session.add(user_progress)
        db.session.commit()

    # Ensure exercise progress entries exist for each exercise
    for i, exercise in enumerate(exercises):
        user_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
        if not user_exercise_progress:
            # Mark the first exercise as available, others as locked
            status = 'available' if i == 0 else 'locked'
            user_exercise_progress = UserExerciseProgress(userid=current_user.userid, exerciseid=exercise.exerciseid, status=status)
            db.session.add(user_exercise_progress)
            db.session.commit()

    # Fetch exercise progress for each exercise
    exercise_progress = [
        UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
        for exercise in exercises
    ]

    # Handle exercise completion
    if request.method == 'POST':
        completed_exercise_id = request.form.get('completed_exercise_id')
        if completed_exercise_id:
            completed_exercise = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=completed_exercise_id).first()
            if completed_exercise and completed_exercise.status != 'completed':
                completed_exercise.status = 'completed'
                db.session.commit()

                # Unlock the next exercise if it exists
                current_exercise_index = next((i for i, ex in enumerate(exercises) if str(ex.exerciseid) == completed_exercise_id), None)
                if current_exercise_index is not None and current_exercise_index < len(exercises) - 1:
                    next_exercise = exercises[current_exercise_index + 1]
                    next_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=next_exercise.exerciseid).first()
                    if next_exercise_progress and next_exercise_progress.status == 'locked':
                        next_exercise_progress.status = 'available'
                        db.session.commit()

                # Redirect to Future You page
                return redirect(url_for('future_you'))

    return render_template("exercise.html", module=module, exercises=exercises, exercise_progress=exercise_progress)


# Your other imports and code here...

def check_if_second_exercise_completed(userid, module_id):
    # Fetch the second exercise dynamically from the module
    second_exercise = Exercise.query.filter_by(moduleid=module_id).order_by(Exercise.exerciseid).offset(1).first()  # This grabs the second exercise based on the module
    if second_exercise:
        user_progress = UserExerciseProgress.query.filter_by(userid=userid, exerciseid=second_exercise.exerciseid).first()
        return user_progress is not None and user_progress.status == 'completed'
    return False



@app.route('/future_you', methods=['GET', 'POST'])
@login_required
def future_you():
    # Get the current user
    userid = current_user.userid  # Assuming `userid` is the primary key for the User model

    # Fetch the current module for the user (from UserModuleProgress)
    user_module_progress = UserModuleProgress.query.filter_by(userid=userid).first()
    if user_module_progress:
        current_module_id = user_module_progress.moduleid
    else:
        current_module_id = None  # Or handle if the user has no progress

    # Check if the second exercise is completed dynamically
    second_exercise_completed = check_if_second_exercise_completed(userid, current_module_id)

    # Fetch career suggestions for the current module or exercise
    if current_module_id:
        career_suggestions = CareerSuggestions.query.filter_by(exerciseid=current_module_id).all()
    else:
        career_suggestions = []  # If no module is found, return an empty list

    if request.method == 'POST':
        if second_exercise_completed:
            # Redirect to the Dashboard if the second exercise is completed
            return redirect(url_for('dashboard'))
        else:
            # Redirect to the exercises page with the current module id
            return redirect(url_for('exercises', module_id=current_module_id))

    return render_template('future_you.html', 
                           second_exercise_completed=second_exercise_completed,
                           career_suggestions=career_suggestions)


# Logout route
@app.route("/logout")
@login_required  # Ensure the user is logged in before logging out
def logout():
    logout_user()  # Logs out the current user
    flash("You have been logged out.", "success")  # Optionally, flash a message
    return redirect(url_for("home"))  # Redirect to the home page or login page



if __name__ == "__main__":
    app.run(debug=True)


