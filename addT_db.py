

from app import app, db, Module  # Import the specific model you want to create
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect

def create_table_module():
    try:
        # Inspect the database and check if the table exists
        inspector = inspect(db.engine)
        
        if not inspector.has_table(Module.__tablename__):
            Module.__table__.create(db.engine)
            print(f"Table {Module.__tablename__} has been created.")
        else:
            print(f"Table {Module.__tablename__} already exists.")
        
    except Exception as e:
        print(f"Error creating the table: {e}")


def add():
    with app.app_context():  # Ensure Flask app context is active
        create_table_module()

if __name__ == "__main__":
    add()
