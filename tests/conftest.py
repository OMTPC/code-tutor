
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
