"""
Class and section forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ClassForm(FlaskForm):
    """Class create/edit form"""
    name = StringField('Class Name', validators=[DataRequired()])
    class_type_id = SelectField('Class Type', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Class')


class SectionForm(FlaskForm):
    """Section create/edit form"""
    name = StringField('Section Name', validators=[DataRequired()])
    teacher_id = SelectField('Class Teacher', coerce=int)
    active = BooleanField('Active', default=True)
    submit = SubmitField('Save Section')
