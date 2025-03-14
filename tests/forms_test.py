
import pytest
from app import app, db, User


def test_registration_invalid(client):
    """Test registration with missing fields."""
    response = client.post('/register', data={  # Missing password
        'username': 'testuser',
        'email': 'testuser@example.com'
    }, follow_redirects=True)
    
    assert b'Password: This field is required.' in response.data

