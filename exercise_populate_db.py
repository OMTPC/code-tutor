from app import db, Exercise, app, Solution



module_id = 1  # This corresponds to "Module 1: Variables & Data Types"

def add_exercise():
    exercise1 = Exercise (moduleid=module_id,  # Associating with the module
    title="Print 'Hello World!'",  # The title of the exercise
    description="""Concept: In this exercise, you'll learn the most basic programming task: 
                   printing a message to the screen. 
                   Explanation: In Python, the print() function is used 
                   to display output in the console. This is the first step to seeing how your 
                   code works in the real world.""",  # Detailed exercise description
    status="available"  # Initial status of the exercise
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


    db.session.add(exercise1)
    db.session.add(exercise2)
    db.session.commit()
    print("Exercise added successfully!")

    # Add plain text solution
    solution1 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_text="print('Hello World!')",  # Solution as plain text
        solution_type='text'  # Indicating that this is a text solution
    )

    solution2 = Solution(
            exerciseid=exercise1.exerciseid,
            solution_text='print("Hello World!")',  # Solution as plain text
            solution_type='text'  # Indicating that this is a text solution
        )

    db.session.add(solution1)
    db.session.add(solution2)
   

    # Add regex solution
    solution3 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_regex=r"print\s*\(\s*['\"]Hello World!['\"]\s*\)",  # Solution as a regex pattern
        solution_type='regex'  # Indicating that this is a regex solution
    )

    db.session.add(solution3)

    solution4 = Solution(
        exerciseid=exercise2.exerciseid,
        solution_regex = r"age\s*=\s*\d+\s*name\s*=\s*['\"].*['\"]\s*height\s*=\s*\d+\.\d+\s*print\s*\(\s*age\s*\)\s*print\s*\(\s*name\s*\)\s*print\s*\(\s*height\s*\)",
        solution_type='regex'  # A regex solution only
    )

    db.session.add(solution4)
    db.session.commit()

    print("Exercise and solutions added successfully!")


# Main function to populate the database
def populate_db():
    with app.app_context():  # Ensure Flask app context is active
       add_exercise()

# Run the script to populate the database
if __name__ == "__main__":
    populate_db()
