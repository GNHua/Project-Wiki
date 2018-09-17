from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired('Please enter your username.')]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired('Please enter your password.')]
    )
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')
    

class ChangePwdForm(FlaskForm):
    old_password = PasswordField(
        'Old Password',
        validators=[DataRequired('Please enter old password.')]
    )
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired('Please enter new password.')]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired('Please enter new password again.')]
    )
    submit = SubmitField('Submit')
