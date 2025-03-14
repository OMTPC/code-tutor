import pytest
from app import app, db, User

def test_user_creation(client):
    """Test user creation and database interaction."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 302


    # Check if the user exists in the database
    user = db.session.query(User).filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'
