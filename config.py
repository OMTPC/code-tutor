"""
Created by: Orlando Caetano
Last Updated: 11/03/2025
Description: 
    Configuration settings for the Code Mentor web application. The `Config` class defines general settings 
    such as the secret key and SQLAlchemy options. The `ProductionConfig` class inherits from `Config` 
    and defines the URI for the production database. The `TestingConfig` class is used for testing purposes 
    and configures an in-memory SQLite database, as well as disabling CSRF protection for testing.

Resources: Please refer to the Reference list for CodeMentor App for the resources used to build this application.
"""

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'MasterKey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Production database
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///codetutorDB.db'  


# Testing database
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  
    WTF_CSRF_ENABLED = False
