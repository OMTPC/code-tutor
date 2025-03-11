
"""
Created by: Orlando Caetano  
Last Updated: 18/02/2025
Description:  
This script is used to populate the Code Tutor database.  
It defines functions to add content to the database and runs them within the Flask app context.  

Resources: Please refer to Reference list for CodeMentor App for the resources used to build this application. 
"""

from app import app, db, Module

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


# Main function to populate the database
def populate_db():
    with app.app_context():  
       add_modules()

# Run the script to populate the database
if __name__ == "__main__":
    populate_db()
