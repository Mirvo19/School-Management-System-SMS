"""
Exam forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class ExamForm(FlaskForm):
    """Exam create/edit form"""
    name = StringField('Exam Name', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    term = SelectField('Term', choices=[
        (1, 'First Term'),
        (2, 'Second Term'),
        (3, 'Third Term')
    ], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Exam')
