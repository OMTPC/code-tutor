"""
Created by: Orlando Caetano
Last update: 14/03/2025
Description: 
    This is a testing setup for the Flask-based Code Mentor web application. 
    It configures the Flask app for testing by setting the 'FLASK_ENV' to 'testing' 
    and sets up a test client using pytest. The database is initialized and cleaned 
    up after each test by creating and dropping tables. This is done in preparation 
    for unit tests that validate the functionality of the Code Mentor app, including 
    user authentication, progress tracking, and career suggestions.

Resources: Please refer to the Reference list for Code Mentor App for the resources used to build this application.
"""

import sys
import os
import pytest

os.environ['FLASK_ENV'] = 'testing'

# Add the root directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

@pytest.fixture
def client():
    # Set up the test client
    app.config['TESTING'] = True
    

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
