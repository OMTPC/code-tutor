"""
Created by: Orlando Caetano
Last update: 14/03/2025
Description: 
    This is a test for the registration functionality of the Flask-based Code Mentor web application. 
    It validates that the registration process correctly handles missing fields, specifically the password field. 
    The test attempts to register a user with an incomplete form (missing the password) and checks for the appropriate 
    error message indicating the required field.

Resources: Please refer to the Reference list for Code Mentor App for the resources used to build this application.
"""

import pytest
from app import app, db, User


def test_registration_invalid(client):
    """Test registration with missing fields."""
    response = client.post('/register', data={  
        'username': 'testuser',
        'email': 'testuser@example.com'
    }, follow_redirects=True)
    
    assert b'Password: This field is required.' in response.data

