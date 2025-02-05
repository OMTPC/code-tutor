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


    db.session.add(exercise1)
    db.session.commit()
    print("Exercise added successfully!")

    # Add plain text solution
    solution1 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_text="print('Hello World!')",  # Solution as plain text
        solution_type='text'  # Indicating that this is a text solution
    )

    db.session.add(solution1)
   

    # Add regex solution
    solution2 = Solution(
        exerciseid=exercise1.exerciseid,
        solution_regex=r"print\(\s*'Hello World!'\s*\)",  # Solution as a regex pattern
        solution_type='regex'  # Indicating that this is a regex solution
    )

    db.session.add(solution2)

    db.session.commit()

    print("Exercise and solutions added successfully!")


# Main function to populate the database
def populate_db():
    with app.app_context():  # Ensure Flask app context is active
       add_exercise()

# Run the script to populate the database
if __name__ == "__main__":
    populate_db()
