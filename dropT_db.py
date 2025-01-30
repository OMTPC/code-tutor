




from app import app, db, Module  # Import db from your app.py where the database and models are defined
 
def drop_table():
    try:
        # Drop the specific table (in this case, the 'Module' table)
        Module.__table__.drop(db.engine)
        print(f"The table {Module.__tablename__} has been dropped.")
        
    except Exception as e:
        print(f"Error dropping table: {e}")


def drop():
    with app.app_context():  # Ensure Flask app context is active
        drop_table()


if __name__ == "__main__":
    drop()
