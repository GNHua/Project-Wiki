from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Regexp, Email


class AddGroupForm(FlaskForm):
    groupname = StringField(
        'Group Name',
        validators=[
            DataRequired('Please enter a group name.'),
            Regexp('^[\w+ ]+$', message='Group name must contain only letters, '
                                        'numbers, underscore, and whitespace.')
        ]
    )
    username = StringField(
        'Username',
        validators=[
            DataRequired('Please enter a username.'),
            Regexp('^[\w+ ]+$', message='Username must contain only letters, '
                                        'numbers, and underscore.')
        ]
    )
    email = StringField(
        'Email address', 
        validators=[
            DataRequired('Please enter an email address.'), 
            Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired('Please enter a password.')]
    )
    add = SubmitField('Add')


class NewUserForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired('Please enter a username.'),
            Regexp('^[\w+ ]+$', message='Username must contain only letters, '
                                        'numbers, and underscore.')
        ]
    )
    email = StringField(
        'Email address', 
        validators=[
            DataRequired('Please enter an email address.'), 
            Email()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired('Please enter a password.')]
    )
    access = SelectField(
        'Access',
        choices=[('Admin', 'Admin'), ('User', 'User'), ('Guest', 'Guest')]
    )
    add = SubmitField('Add')


class ExistingUserForm(FlaskForm):
    email = StringField(
        'Email address', 
        validators=[
            DataRequired('Please enter an email address.'), 
            Email()
        ]
    )
    password = PasswordField('Password')
    access = SelectField(
        'Access',
        choices=[('Admin', 'Admin'), ('User', 'User'), ('Guest', 'Guest')]
    )
    add = SubmitField('Add')
    remove = SubmitField('Remove')


class PageDeletionForm(FlaskForm):
    page_id = StringField(
        'Page id',
        validators=[DataRequired('Please choose a page.')]
    )
    submit = SubmitField('Delete')


class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Search')


class FileDeletionForm(FlaskForm):
    file_id = IntegerField(
        'File id',
        validators=[DataRequired('Please choose a file.')]
    )
    submit = SubmitField('Delete')
