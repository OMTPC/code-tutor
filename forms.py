"""
Created by: Orlando Caetano  
Last Updated: 14/02/2025
Description:  
This module contains Flask-WTF forms used for user authentication in the Code Mentor application.  
It includes a login form for user authentication and a registration form for new user sign-ups.  
The forms enforce data validation using WTForms validators to ensure data integrity.  

Resources: Please refer to Reference list for CodeMentor App for the resources used to build this application. 
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length

# Login Form: Used for user authentication
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField("Remember Me")


# Registration Form: Used for new user registration
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
