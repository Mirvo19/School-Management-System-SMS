"""
Mark forms
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import Optional, NumberRange


class MarkForm(FlaskForm):
    """Mark entry form"""
    t1 = IntegerField('Test 1', validators=[Optional(), NumberRange(min=0, max=100)])
    t2 = IntegerField('Test 2', validators=[Optional(), NumberRange(min=0, max=100)])
    t3 = IntegerField('Test 3', validators=[Optional(), NumberRange(min=0, max=100)])
    exams = IntegerField('Exam', validators=[Optional(), NumberRange(min=0, max=100)])
    teacher_remark = StringField('Teacher Remark')
    submit = SubmitField('Save Marks')
