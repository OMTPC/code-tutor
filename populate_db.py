# populate_db.py

from app import app, db, Module, Exercise


"""
# Function to add modules
def add_modules():
    module1 = Module(title="Variables & Data Types", description="Learn about different types of variables and data structures in programming.")
    module2 = Module(title="Control Flow", description="Master if/else statements, loops, and conditional programming.")
    module3 = Module(title="Functionss", description="Understanding functions, parameters, and return values.")

    db.session.add(module1)
    db.session.add(module2)
    db.session.add(module3)
    db.session.commit()
    print("Modules added successfully!")

"""

def add_exercise():
    exercise1 = Exercise(moduleid=1, title="Exercise 1: Hello, Python!", description="Write a Python script that prints Hello, Python World! to the console", status="locked")
    exercise2 = Exercise(moduleid=1, title="Exercise 2: Introduction to Variables)", description="In this exercise, you'll learn about variables in Python. Define a variable and print it.", status="locked")
    
    db.session.add(exercise1)
    db.session.add(exercise2)
    
    db.session.commit()
    print("Modules added successfully!")



# Main function to populate the database
def populate_db():
    with app.app_context():  # Ensure Flask app context is active
       # add_modules()
        add_exercise()

# Run the script to populate the database
if __name__ == "__main__":
    populate_db()
