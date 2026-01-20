"""
Profile forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ProfileForm(FlaskForm):
    """User profile edit form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=191)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=100)])
    phone2 = StringField('Alternate Phone', validators=[Length(max=100)])
    address = TextAreaField('Address')
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    """Password change form"""
    current_password = StringField('Current Password', validators=[DataRequired()])
    new_password = StringField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
