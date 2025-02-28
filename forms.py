from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Length(1, 64), Email(message='Email address is not valid')])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Length(1, 64), Email(message='Email address is not valid')])
    password_hash = PasswordField('Password', validators=[DataRequired(), Length(6,16), EqualTo('password_hash2', message='Password did not match.')])
    password_hash2 = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Register Account')