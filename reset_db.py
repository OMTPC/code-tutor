from app import db, app, User, Module, Exercise, UserModuleProgress, UserExerciseProgress


def reset_database():
    try:
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")

        # Create new tables
        db.create_all()
        print("New tables created.")

        print("Tables in database:", db.metadata.tables.keys())  

        
    except Exception as e:
        print(f"Error resetting database: {e}")



def reset():
    with app.app_context():  # Ensure Flask app context is active
        reset_database()


if __name__ == "__main__":
    reset()
