"""
Created by: Orlando Caetano
last update: 10/03/2025
Description: 
    This is a Flask-based web application for Code Mentor, designed to help novice programmers 
    learn Python through structured exercises and modules. with a future you page that displays
    career suggestions and coding projects based on the user's progress. The application also
    includes an API to check user code for industry challenges and career suggestions.
    
Resources: Please refer to Reference list for CodeMentor App for the resources used to build this application.
"""

#-------------------------------------------Imports-------------------------------------------------#
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from forms import LoginForm, RegisterForm
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import re
import sys
import io
import os
from config import ProductionConfig, TestingConfig

# Initialize Flask app
app = Flask(__name__)

# Determine the environment and load the correct configuration
if os.getenv("FLASK_ENV") == "testing":
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(ProductionConfig)


# Print the current configuration for debugging purposes
print(f"Running with config: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Secret key for security
#app.config["SECRET_KEY"] = "MasterKey"

# Database configuration (SQLite)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///codetutorDB.db"  
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  
login_manager.login_message = "Please log in to access this page."

# Load user session from database
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))  


# -------------------------------------------database models-------------------------------------------------#

# User table
class User(UserMixin,db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)  
    registered_at = db.Column(db.DateTime, default=func.now)  

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
    
    user_progress = db.relationship('UserExerciseProgress', backref='exercise', lazy=True)

    def __repr__(self):
        return f"Exercise('{self.title}', '{self.status}')"


# Exercises solution Table
class Solution(db.Model):
    solutionid = db.Column(db.Integer, primary_key=True)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=False)
    solution_text = db.Column(db.Text, nullable=True)  
    solution_regex = db.Column(db.Text, nullable=True)  
    solution_type = db.Column(db.Enum('text', 'regex', name='solution_type'), nullable=False, default='text') 
    expected_output = db.Column(db.Text, nullable=True)  

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


#Career suggestions table
class CareerSuggestions(db.Model):
    CSid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=True)  
    keyresponsibilities = db.Column(db.Text, nullable=True)

    exercise = db.relationship('Exercise', backref='career_suggestions', lazy=True)  
    
    def __repr__(self):
        return f"<CareerSuggestion {self.title}>"


# Industry Challenge Table
class IndustryChallenge(db.Model):
    ICid = db.Column(db.Integer, primary_key=True)
    challenge_text = db.Column(db.Text, nullable=False)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=False)  
    example_solution = db.Column(db.Text, nullable=True)
    default_code = db.Column(db.Text, nullable=True)

    exercise = db.relationship('Exercise', backref='industry_challenges', lazy=True)

    def __repr__(self):
        return f"<IndustryChallenge {self.challenge_text[:50]}>"


# Career Story Table
class CareerStory(db.Model):
    CStoryid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    exerciseid = db.Column(db.Integer, db.ForeignKey('exercise.exerciseid'), nullable=True)  
    CSid = db.Column(db.Integer, db.ForeignKey('career_suggestions.CSid'), nullable=True)  

    exercise = db.relationship('Exercise', backref='career_story', lazy=True)  
    career_suggestion = db.relationship('CareerSuggestions', backref='career_story', lazy=True)
    

    def __repr__(self):
        return f"<CareerStory {self.title}>"



#----------------------------------------------------------API Routes-------------------------------------------------#

# API Route to fetch career suggestions
@app.route('/api/career_suggestions/<int:exerciseid>', methods=['GET'])
def get_career_suggestions(exerciseid):
    
    career_suggestions = CareerSuggestions.query.filter_by(exerciseid=exerciseid).all()
    
    if career_suggestions:
        return jsonify([{
            "CSid": suggestion.CSid,
            "title": suggestion.title,
            "description": suggestion.description,
            "key_responsibilities": suggestion.keyresponsibilities if hasattr(suggestion, 'keyresponsibilities') else "Not available"
        } for suggestion in career_suggestions])
    else:
        return jsonify({"error": "No career suggestions found for this exercise"}), 404


# API Route to fetch key responsibilities for a career suggestion
@app.route('/api/career_suggestions/responsibilities/<int:CSid>', methods=['GET'])
def get_key_responsibilities(CSid):
    career = CareerSuggestions.query.get(CSid)
    if career:
        return jsonify({"keyresponsibilities": career.keyresponsibilities})
    else:
        return jsonify({"error": "Career suggestion not found"}), 404


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


# API Route to fetch the solution for an exercise
@app.route('/api/get_exercises', methods=['GET'])
def get_exercises():
    # Fetch exercises from the database
    exercises = Exercise.query.all()
    
    exercises_list = []
    for exercise in exercises:
        exercise_data = {
            'exerciseid': exercise.exerciseid,
            'moduleid': exercise.moduleid,
            'title': exercise.title,
            'exercise_number': exercise.exerciseid  
        }
        exercises_list.append(exercise_data)
    
    return jsonify(exercises_list)


# API Route to execute user code for indutry challenges
@app.route('/run_code', methods=['POST'])
def run_code():
    data = request.json
    user_code = data.get("code", "")

    # Check if the user is trying to use a while loop
    if "while" in user_code:
        return jsonify({"output": "Error: while loops are not allowed!"})
    
    # Restricted execution environment
    allowed_builtins = {"print": print, "range": range, "len": len, "input": lambda prompt="": input_values.pop(0) if input_values else ""}
    
    input_values = data.get("inputs", [])

    output_capture = io.StringIO()
    sys.stdout = output_capture

    try:
        exec(user_code, {"__builtins__": allowed_builtins}, {})  
        output = output_capture.getvalue()
    except Exception as e:
        output = f"Error: {str(e)}"
    
    sys.stdout = sys.__stdout__

    return jsonify({"output": output})


# Function to check the user's code against the expected solution
def check_solution(user_code, exercise_id):
    
    solutions = Solution.query.filter_by(exerciseid=exercise_id).all()

    for solution in solutions:
        if solution.solution_type == 'text' and solution.solution_text.strip().lower() == user_code.strip().lower():
            return "Correct!"

        if solution.solution_type == 'regex':
            pattern = re.compile(solution.solution_regex)
            if pattern.fullmatch(user_code.strip()):
                return "Correct!"

    return "Incorrect. Please try again."  


# API Route to check the user's code against the expected solution
@app.route('/check_code', methods=['POST'])
def check_code():
    data = request.get_json()

    if not data or 'code' not in data or 'exercise_id' not in data:
        return jsonify({'result': 'Error: Missing code or exercise ID'}), 400  

    user_code = data['code']
    exercise_id = data['exercise_id']

    result = check_solution(user_code, exercise_id)

    if result == "Correct!":
        progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise_id).first()
        if not progress:
            progress = UserExerciseProgress(userid=current_user.userid, exerciseid=exercise_id, status='completed')
            db.session.add(progress)
        else:
            progress.status = 'completed'

        db.session.commit()

        next_exercise = Exercise.query.filter(Exercise.exerciseid > exercise_id, Exercise.moduleid == Exercise.query.filter_by(exerciseid=exercise_id).first().moduleid).order_by(Exercise.exerciseid).first()
        
        if next_exercise:
            next_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=next_exercise.exerciseid).first()
            if next_progress:
                next_progress.status = 'available'
            else:
                next_progress = UserExerciseProgress(userid=current_user.userid, exerciseid=next_exercise.exerciseid, status='available')
                db.session.add(next_progress)
            db.session.commit()

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

    solution_entry = Solution.query.filter_by(exerciseid=exercise_id).first()

    expected_output_text = solution_entry.expected_output if solution_entry and solution_entry.expected_output else "No expected output available."
    
    return jsonify({'result': result, 'expected_output': expected_output_text})


# API Route to fetch career suggestions for a given exercise
@app.route('/api/career_suggestions/stories/<int:CSid>', methods=['GET'])
@login_required
def get_career_stories(CSid):
    
    career_stories = CareerStory.query.filter_by(CSid=CSid).all()

    if not career_stories:
        return jsonify({"error": "No career stories found for this suggestion."})

    stories_data = [
        {
            "CStoryid": story.CStoryid,  
            "title": story.title,
            "description": story.description
        } 
        for story in career_stories
    ]

    return jsonify({"career_stories": stories_data})


#----------------------------------------------------------Routes-------------------------------------------------#

# Homepage route
@app.route("/")
def home():
    current_year = datetime.datetime.now().year
    return render_template("index.html", year = current_year)


# Register route - allows users to register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()  
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))
        
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


# Dashboard route - displays the user's progress and modules
@app.route("/dashboard")
@login_required
def dashboard():
    user_modules = []
    modules = Module.query.all()

    first_exercise_completed = UserExerciseProgress.query.filter_by(
        userid=current_user.userid, exerciseid=1, status='completed'
    ).first() is not None

    for module in modules:
        user_module_progress = UserModuleProgress.query.filter_by(
            userid=current_user.userid, moduleid=module.moduleid
        ).first()

        exercises = Exercise.query.filter_by(moduleid=module.moduleid).all()
        completed_exercises = sum(
            1 for exercise in exercises if UserExerciseProgress.query.filter_by(
                userid=current_user.userid, exerciseid=exercise.exerciseid, status='completed'
            ).first()
        )

        progress = int((completed_exercises / len(exercises)) * 100) if exercises else 0

        # Determine module status
        if module.moduleid == 1:
            module_status = 'available' 
        else:
            previous_module_progress = UserModuleProgress.query.filter_by(
                userid=current_user.userid, moduleid=module.moduleid - 1, status='completed'
            ).first()

            if previous_module_progress:
                module_status = 'available'
            else:
                module_status = 'locked'

        if completed_exercises == len(exercises):
            module_status = 'completed'

        if user_module_progress:
            user_module_progress.status = module_status
        else:
            user_module_progress = UserModuleProgress(userid=current_user.userid, moduleid=module.moduleid, status=module_status)
            db.session.add(user_module_progress)

        db.session.commit()

        user_modules.append({
            'module': module,
            'status': module_status,
            'progress': progress
        })

    return render_template("dashboard.html", user_modules=user_modules, first_exercise_completed=first_exercise_completed)


# Module intro route - displays the module introduction
@app.route('/module_intro/<int:module_id>', methods=['GET', 'POST'])
@login_required
def module_intro(module_id):
    
    module = Module.query.get_or_404(module_id)
    
    user_progress = UserModuleProgress.query.filter_by(userid=current_user.userid, moduleid=module_id).first()

    if request.method == 'POST':
        # If the user clicks to start the first exercise, redirect to exercises page
        return redirect(url_for('exercises', module_id=module_id))

    return render_template('module_intro.html', module=module)


# Module exercises route - displays the module exercises
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

    for i, exercise in enumerate(exercises):
        user_exercise_progress = UserExerciseProgress.query.filter_by(userid=current_user.userid, exerciseid=exercise.exerciseid).first()
        if not user_exercise_progress:
            status = 'available' if i == 0 else 'locked'
            user_exercise_progress = UserExerciseProgress(userid=current_user.userid, exerciseid=exercise.exerciseid, status=status)
            db.session.add(user_exercise_progress)
            db.session.commit()

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

                return redirect(url_for('future_you'))

    return render_template("exercise.html", module=module, exercises=exercises, exercise_progress=exercise_progress)


# function to check if the second exercise is completed (for Exercise or dashboard button)
def check_if_second_exercise_completed(userid, module_id):
    
    second_exercise = Exercise.query.filter_by(moduleid=module_id).order_by(Exercise.exerciseid).offset(1).first()  # This grabs the second exercise based on the module
    if second_exercise:
        user_progress = UserExerciseProgress.query.filter_by(userid=userid, exerciseid=second_exercise.exerciseid).first()
        return user_progress is not None and user_progress.status == 'completed'
    return False


# Future you route - displays career suggestions; Industry challenges and coding projects
@app.route('/future_you', methods=['GET', 'POST'])
@login_required
def future_you():
    
    userid = current_user.userid  

    # Fetch the current module for the user (from UserModuleProgress)
    user_module_progress = UserModuleProgress.query.filter_by(userid=userid).first()
    if user_module_progress:
        current_module_id = user_module_progress.moduleid
    else:
        current_module_id = None  

    second_exercise_completed = check_if_second_exercise_completed(userid, current_module_id)

    exercises = Exercise.query.all()

    # Fetch completed exercises for the current user (from UserExerciseProgress)
    completed_exercises = UserExerciseProgress.query.filter_by(userid=userid, status='completed').all()

    career_suggestions = []
    seen_exercise_ids = set()  

    # Loop through the completed exercises
    for completed_exercise in completed_exercises:
        exercise = Exercise.query.get(completed_exercise.exerciseid)
        if exercise and completed_exercise.status == 'completed' and completed_exercise.exerciseid not in seen_exercise_ids:
            # Fetch career suggestions for this specific exercise
            suggestions = CareerSuggestions.query.filter_by(exerciseid=exercise.exerciseid).all()
            career_suggestions.extend(suggestions)  
            seen_exercise_ids.add(completed_exercise.exerciseid)  

    
    completed_exercise_ids = {ex.exerciseid for ex in completed_exercises}

    # Add **all exercises** to be displayed, with status for enabling/disabling buttons
    exercises_with_status = []
    for exercise in exercises:
        exercises_with_status.append({
            'exerciseid': exercise.exerciseid,
            'title': exercise.title,
            'is_completed': exercise.exerciseid in completed_exercise_ids  
        })

    if request.method == 'POST':
        if second_exercise_completed:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('exercises', module_id=current_module_id))

    all_exercises_completed = len(completed_exercise_ids) == len(exercises)

    # Coding projects to display
    coding_projects = []
    if all_exercises_completed:
        coding_projects = [
            {
                "id": 1,
                "title": "To-do List App",
                "description": "A simple task management application.",
                "concepts": ["print", "if-statements", "loops"],
                "demoCode": '''
    # Simple Todo List
    tasks = []

    def add_task(task):
        tasks.append(task)
        print(f"Added task: {task}")

    def list_tasks():
        if len(tasks) == 0:
            print("No tasks!")
            return
        print("Your tasks:")
        for i, task in enumerate(tasks):
            print(f"{i + 1}. {task}")

    add_task("Learn Python")
    add_task("Build projects")
    list_tasks()
                '''
            },
            {
                "id": 2,
                "title": "Number Guessing Game",
                "description": "Interactive game using conditions.",
                "concepts": ["print", "if-statements", "loops"],
                "demoCode": '''
    # Number Guessing Game
    secret = 7
    guess = None

    while guess != secret:
        guess = int(input("Guess the number: "))
        if guess < secret:
            print("Too low!")
        elif guess > secret:
            print("Too high!")
        else:
            print("You got it!")
                '''
            },
            {
                "id": 3,
                "title": "Calculator",
                "description": "Basic arithmetic operations using functions.",
                "concepts": ["print", "if-statements"],
                "demoCode": '''
    # Simple Calculator
    def calculate(a, b, op):
        if op == '+':
            print(f"{a} + {b} = {a + b}")
        elif op == '-':
            print(f"{a} - {b} = {a - b}")
        elif op == '*':
            print(f"{a} * {b} = {a * b}")
        elif op == '/':
            print(f"{a} / {b} = {a / b}")
        else:
            print("Unsupported operation")

    calculate(5, 3, '+')
    calculate(10, 4, '*')
                '''
            }
        ]

    return render_template('future_you.html', 
                           second_exercise_completed=second_exercise_completed,
                           career_suggestions=career_suggestions,
                           exercises_with_status=exercises_with_status,
                           coding_projects=coding_projects,
                           all_exercises_completed=all_exercises_completed)



# Industry Challenges route - displays the industry challenges exercise details and code editor
@app.route('/industry_challenges/<int:exercise_id>', methods=['GET'])
@login_required
def industry_challenges(exercise_id):
    # Fetch the challenge related to the exercise
    challenge = IndustryChallenge.query.filter_by(exerciseid=exercise_id).first()

    if challenge:
        return render_template('industry_challenges.html', industry_challenges=[challenge])
    else:
        return render_template('industry_challenges.html', industry_challenges=[])


# Logout route
@app.route("/logout")
@login_required  
def logout():
    logout_user()  
    flash("You have been logged out.", "success")  
    return redirect(url_for("home"))  


# start the Flask development server with debugging enabled
if __name__ == "__main__":
    app.run(debug=True)


