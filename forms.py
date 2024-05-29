"""
forms.py

This module defines forms for a Flask web application using Flask-WTF and WTForms.
It includes custom validation to ensure the input data adheres to specified constraints.

Classes:
    UploadForm
    SignUpForm

Functions:
    hashtags(form, field)
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Email
import re

def hashtags(form, field):
    """
    Custom validator to check the format and number of tags in the 'tags' field.

    Args:
        form (FlaskForm): The form containing the field.
        field (Field): The field to validate.

    Raises:
        ValidationError: If any tag does not start with a hashtag (#) or if there are more than 5 tags.

    """
    value = field.data
    if not value:
        return
    tags = re.findall(r'#?\w+', value)

    if not all(item.startswith("#") for item in tags):
        raise ValidationError('Tags must start with a hashtag(#)')
    elif len(tags) > 5:
        raise ValidationError('Tags must not contain more than 5 items')

    field.data = ''.join(tags)

class UploadForm(FlaskForm):
    """
    Form for uploading content. It includes fields for user ID, title, tags, and description.

    Fields:
        user_id (StringField): User ID field, must be exactly 36 characters long.
        title (StringField): Title field, must be between 1 and 30 characters long.
        tags (StringField): Tags field, validated with the custom 'hashtags' function.
        description (TextAreaField): Description field, must not exceed 255 characters.
    """
    class Meta:
        csrf = False

    user_id = StringField('User ID', validators=[DataRequired(), Length(min=36, max=36)])
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=30)])
    tags = StringField('Tags', validators=[Length(max=255), hashtags])
    description = TextAreaField('Description', validators=[Length(max=255)])

class SignUpForm(FlaskForm):
    class Meta:
        csrf = False

    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=30)])
    email = StringField('Email', validators=[DataRequired(), Length(max=50), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
