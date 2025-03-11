"""
Created by: Orlando Caetano
Last Updated: 18/02/2025
Description: This script adds exercises and their respective solutions to the Code Mentor database. It is used to populate 
the database with initial data, specifically for Module 1: Variables & Data Types.

Usage: Run the script as a standalone file to populate the database.

Resources: Please refer to References.txt for the resources used to build this application.
"""

from app import db, Exercise, app, Solution

# Define the module ID for the exercises
module_id = 1  

# Function to add exercises and solutions to the database
def add_exercise():
    exercise1 = Exercise (moduleid=module_id,  
    title="Print 'Hello World!'", 
    description="""Concept: In this exercise, you'll learn the most basic programming task: 
                   printing a message to the screen. 
                   Explanation: In Python, the print() function is used 
                   to display output in the console. This is the first step to seeing how your 
                   code works in the real world.""",  
    status="available"  
    )

    exercise2 = Exercise (moduleid = module_id,
                          title = "Working with Variables ",
                          description = """Concept: Now, we’ll learn how to store information in variables and work with different types of data.
                          Explanation: Variables are like containers that hold values. These values can be numbers, text, or other types of data. 
                          You can also perform operations with them, like printing their value or doing basic calculations.
                          1.	Declare three variables:
                            age: store an integer value, e.g., 25.
                            name: store a string value, e.g., "Alice".
                            height: store a floating-point number, e.g., 5.6.
                          2.	Print each of these variables to the console""",
                          status = "locked"
                        )

    # Add exercises to the database
    db.session.add(exercise1)
    db.session.add(exercise2)
    db.session.commit()
    print("Exercise added successfully!")

    # Add text solutions
    solution1 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_text="print('Hello World!')",  
        solution_type='text'  
    )

    solution2 = Solution(
            exerciseid=exercise1.exerciseid,
            solution_text='print("Hello World!")',  
            solution_type='text' 
        )

    db.session.add(solution1)
    db.session.add(solution2)
   

    # Add regex solution
    solution3 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_regex=r"print\s*\(\s*['\"]Hello World!['\"]\s*\)",  
        solution_type='regex'  
    )

    db.session.add(solution3)

    solution4 = Solution(
        exerciseid=exercise2.exerciseid,
        solution_regex = r"age\s*=\s*\d+\s*name\s*=\s*['\"].*['\"]\s*height\s*=\s*\d+\.\d+\s*print\s*\(\s*age\s*\)\s*print\s*\(\s*name\s*\)\s*print\s*\(\s*height\s*\)",
        solution_type='regex'  
    )

    db.session.add(solution4)
    db.session.commit()

    print("Exercise and solutions added successfully!")


# Main function to populate the database
def populate_db():
    with app.app_context():  
       add_exercise()

# Run the script to populate the database
if __name__ == "__main__":
    populate_db()
