from app import db  # Import the db instance from app.py
from datetime import datetime

# User model
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(80), unique=True, nullable=False)  # Unique username
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique email
    password = db.Column(db.String(200), nullable=False)  # Encrypted password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for user creation
    
    def __repr__(self):
            return f"<User {self.username}>"
