import pytest
from app import app

def test_home_page(client):
    """Test home route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Start Your Python Journey Today' in response.data  # Updated to match your HTML content


def test_register(client):
    """Test registration route"""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123',
    })
    assert response.status_code == 200
