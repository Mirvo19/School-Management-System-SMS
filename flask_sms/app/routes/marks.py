"""
Marks/Grades management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Mark, Exam, Subject, StudentRecord, MyClass, db
from app.forms.mark_forms import MarkForm
from app.utils.helpers import teacher_or_admin_required

marks_bp = Blueprint('marks', __name__)


@marks_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """Marks management page"""
    exams = Exam.query.all()
    subjects = Subject.query.all()
    classes = MyClass.query.all()
    return render_template('marks/index.html', exams=exams, subjects=subjects, classes=classes)


@marks_bp.route('/manage/<int:exam_id>/<int:subject_id>/<int:class_id>')
@login_required
@teacher_or_admin_required
def manage(exam_id, subject_id, class_id):
    """Manage marks for exam, subject, and class"""
    exam = Exam.query.get_or_404(exam_id)
    subject = Subject.query.get_or_404(subject_id)
    students = StudentRecord.query.filter_by(my_class_id=class_id).all()
    
    marks = {}
    for student in students:
        mark = Mark.query.filter_by(
            exam_id=exam_id,
            subject_id=subject_id,
            student_id=student.user_id
        ).first()
        marks[student.id] = mark
    
    return render_template('marks/manage.html',
                         exam=exam, subject=subject,
                         students=students, marks=marks)


@marks_bp.route('/save', methods=['POST'])
@login_required
@teacher_or_admin_required
def save():
    """Save marks"""
    exam_id = request.form.get('exam_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    class_id = request.form.get('class_id', type=int)
    
    students = StudentRecord.query.filter_by(my_class_id=class_id).all()
    
    for student in students:
        mark = Mark.query.filter_by(
            exam_id=exam_id,
            subject_id=subject_id,
            student_id=student.user_id
        ).first()
        
        if not mark:
            mark = Mark(
                exam_id=exam_id,
                subject_id=subject_id,
                student_id=student.user_id,
                my_class_id=class_id,
                section_id=student.section_id,
                year=Exam.query.get(exam_id).year
            )
            db.session.add(mark)
        
        # Update marks from form
        mark.t1 = request.form.get(f't1_{student.id}', type=int)
        mark.t2 = request.form.get(f't2_{student.id}', type=int)
        mark.t3 = request.form.get(f't3_{student.id}', type=int)
        mark.exams = request.form.get(f'exams_{student.id}', type=int)
        
        # Calculate total
        mark.total = (mark.t1 or 0) + (mark.t2 or 0) + (mark.t3 or 0) + (mark.exams or 0)
    
    db.session.commit()
    flash('Marks saved successfully!', 'success')
    return redirect(url_for('marks.manage',
                          exam_id=exam_id,
                          subject_id=subject_id,
                          class_id=class_id))
