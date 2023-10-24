from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, Length


class SignUpForm(FlaskForm):
    '''Form for creating new users.'''

    first_name = StringField('First Name', validators=[DataRequired(
        message='First name is required, and it must not contain any spaces.')])
    last_name = StringField('Last Name', validators=[DataRequired(
        message='Last name is required, and it must not contain any spaces.')])
    email = EmailField('Email', validators=[Email(
        message='Please enter a valid email address.')])
    profile_picture = StringField(
        'Profile Picture URL', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired(
        message='Password is required, and it must not contain spaces.'), Length(min=8, message='Password must be at least 8 characters long.')])


class LoginForm(FlaskForm):
    '''Form for logging in users.'''

    email = EmailField('Email', validators=[Email(
        message='Please enter a valid email address.')])
    password = PasswordField('Password', validators=[
                             DataRequired(message='Password is required.')])


class WishlistForm(FlaskForm):
    '''Form for creating a wishlist.'''

    name = StringField('Name', validators=[DataRequired(
        message='Name is required, and it must not contain any spaces.')])
    description = TextAreaField('Description', validators=[
                                DataRequired('Description is required.')])
