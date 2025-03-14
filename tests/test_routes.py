"""
Created by: Orlando Caetano
Last update: 14/03/2025
Description: 
    This file contains tests for the Flask-based Code Mentor web application. 
    It includes tests for the home route and registration route of the application.

Resources: Please refer to the Reference list for Code Mentor App for the resources used to build this application.
"""


import pytest
from app import app

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Start Your Python Journey Today' in response.data 


def test_register(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123',
    })
    assert response.status_code == 200
