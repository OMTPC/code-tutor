"""
Created by: Orlando Caetano
Last update: 14/03/2025
Description: 
    This test verifies the user creation functionality and the interaction between the Flask-based 
    Code Mentor web application and the database. It simulates a user registration with all required 
    fields, and checks for a successful redirection after the registration. 

Resources: Please refer to the Reference list for Code Mentor App for the resources used to build this application.
"""

import pytest
from app import app, db, User

def test_user_creation(client):
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
