


import pytest
from app import app, db, CareerSuggestions, Exercise, Solution


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()  # Create the tables
        with app.test_client() as client:
            yield client
        db.drop_all()  # Clean up after tests

def test_get_career_suggestions(client):
    response = client.get('/api/career_suggestions/1')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_key_responsibilities(client):
    response = client.get('/api/career_suggestions/responsibilities/1')
    assert response.status_code == 200
    assert 'keyresponsibilities' in response.json

def test_get_exercise(client):
    response = client.get('/api/exercise/1')
    assert response.status_code == 200
    assert 'exerciseid' in response.json

def test_get_exercises(client):
    response = client.get('/api/get_exercises')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_run_code(client):
    response = client.post('/run_code', json={"code": "print('Hello, World!')"})
    assert response.status_code == 200
    assert 'output' in response.json

def test_check_code(client):
    response = client.post('/check_code', json={"code": "print('Hello, World!')", "exercise_id": 1})
    assert response.status_code == 200
    assert 'result' in response.json

def test_get_career_stories(client):
    response = client.get('/api/career_suggestions/stories/1')
    assert response.status_code == 200
    assert isinstance(response.json['career_stories'], list)