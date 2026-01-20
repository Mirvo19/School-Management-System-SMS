"""
Subject forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class SubjectForm(FlaskForm):
    """Subject create/edit form"""
    name = StringField('Subject Name', validators=[DataRequired()])
    my_class_id = SelectField('Class', coerce=int)
    teacher_id = SelectField('Teacher', coerce=int)
    submit = SubmitField('Save Subject')
