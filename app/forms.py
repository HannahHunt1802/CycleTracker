from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Regexp
from .models import User
import re

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid email address."), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=30), Regexp(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])', message="Password must contain at least one uppercase, digit and special character.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField('Register')

    def validate_email(self, email):
        # checks if user already exists
        email=email.data.strip()
        if User.query.filter_by(email=email).first():
            raise ValidationError('Account already exists.')

    def validate_password(self, password):
        #check if password relates to the username (ignoring case)
        password = password.data
        name = self.name.data.strip().lower()
        main_username = name.split('@')[0]

        if main_username in password.lower():
            raise ValidationError('Password must not contain your username.')

        #password should not contain values from the blacklist
        forbidden_passwords = ["Password123$", "Qwerty123!", "Adminadmin1@", "weLcome123!"]
        if password.lower() in [p.lower() for p in forbidden_passwords]:
            raise ValidationError('Password must not be a common password.')

        # avoid repeated character sequences in cases where 3 or more are in a row
        if re.search(r"(.)\1\1", password):
            raise ValidationError('Password must not contain three or more repeated characters.')

        if ' ' in password:
            raise ValidationError('Password must not contain whitespace.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid email address.")])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LogoutForm(FlaskForm):
    #empty to provide csrf token for logout button
    submit = SubmitField('Logout')