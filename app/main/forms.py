from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length


class BasicEditForm(FlaskForm):
    textArea = TextAreaField('Edit')
    submit = SubmitField('Save Changes')


class WikiEditForm(BasicEditForm):
    current_version = IntegerField('Current version')


class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Search')


class CommentForm(FlaskForm):
    textArea = TextAreaField('Edit', 
        validators=[DataRequired('Comment is empty.')]
        )
    submit = SubmitField('Submit')
    

class RenameForm(FlaskForm):
    new_title = StringField(
        'New page title',
        validators=[
            DataRequired('Please enter a new page title.'),
            Length(max=256, message='Page title must be 256 characters or less.')
        ]
    )
    submit = SubmitField('Rename')


class UploadForm(FlaskForm):
    file = FileField('File')
    upload = SubmitField('Upload')


class VersionRecoverForm(FlaskForm):
    version = IntegerField(
        'Recover version',
        validators=[DataRequired('Please enter a version number.')]
    )
    submit = SubmitField('Submit')
