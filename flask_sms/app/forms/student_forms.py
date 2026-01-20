"""
Student forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class StudentForm(FlaskForm):
    """Student create/edit form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=191)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password')
    phone = StringField('Phone Number')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    address = TextAreaField('Address')
    
    my_class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section', coerce=int, validators=[DataRequired()])
    my_parent_id = SelectField('Parent/Guardian', coerce=int)
    
    adm_no = StringField('Admission Number', validators=[DataRequired()])
    year_admitted = IntegerField('Year Admitted', validators=[DataRequired()])
    session = StringField('Session', validators=[DataRequired()])
    house = StringField('House')
    age = IntegerField('Age')
    
    blood_group_id = SelectField('Blood Group', coerce=int)
    
    submit = SubmitField('Save Student')


class PromotionForm(FlaskForm):
    """Student promotion form"""
    from_class = SelectField('From Class', coerce=int, validators=[DataRequired()])
    from_section = SelectField('From Section', coerce=int, validators=[DataRequired()])
    to_class = SelectField('To Class', coerce=int, validators=[DataRequired()])
    to_section = SelectField('To Section', coerce=int, validators=[DataRequired()])
    from_session = StringField('From Session', validators=[DataRequired()])
    to_session = StringField('To Session', validators=[DataRequired()])
    submit = SubmitField('Promote Students')
