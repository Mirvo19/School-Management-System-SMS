"""
User management forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UserForm(FlaskForm):
    """User create/edit form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=191)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password')
    user_type = SelectField('User Type', choices=[
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('accountant', 'Accountant'),
        ('librarian', 'Librarian')
    ], validators=[DataRequired()])
    
    phone = StringField('Phone Number')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    address = TextAreaField('Address')
    
    submit = SubmitField('Save User')


class StaffForm(FlaskForm):
    """Staff record form"""
    code = StringField('Staff Code')
    emp_date = DateField('Employment Date', format='%Y-%m-%d')
    submit = SubmitField('Save Staff Record')
