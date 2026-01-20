"""
Marks/Grades management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Mark, Exam, Subject, StudentRecord, MyClass, User, db
from app.forms.mark_forms import MarkForm
from app.utils.helpers import teacher_or_admin_required

from datetime import datetime

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
        mark.exams = request.form.get(f'exams_{student.id}', type=int)
        
        # Calculate total
        mark.total = (mark.t1 or 0) + (mark.exams or 0)
    
    db.session.commit()
    flash('Marks saved successfully!', 'success')
    return redirect(url_for('marks.manage',
                          exam_id=exam_id,
                          subject_id=subject_id,
                          class_id=class_id))


def calculate_grade(percentage):
    if percentage >= 90: return 'A'
    elif percentage >= 80: return 'B'
    elif percentage >= 70: return 'C'
    elif percentage >= 60: return 'D'
    elif percentage >= 50: return 'E'
    else: return 'F'

def calculate_gpa(percentage):
    if percentage >= 90: return 4.0
    elif percentage >= 80: return 3.6
    elif percentage >= 70: return 3.2
    elif percentage >= 60: return 2.8
    elif percentage >= 50: return 2.4
    else: return 0.0

@marks_bp.route('/results/<int:exam_id>/<int:class_id>')
@login_required
@teacher_or_admin_required
def class_results(exam_id, class_id):
    """Generate class results report"""
    exam = Exam.query.get_or_404(exam_id)
    my_class = MyClass.query.get_or_404(class_id)
    students = StudentRecord.query.filter_by(my_class_id=class_id).all()
    subjects = Subject.query.filter_by(my_class_id=class_id).all()
    
    # If no specific subjects for class, getting all subjects (fallback logic if needed)
    if not subjects:
        subjects = Subject.query.all()

    results = []
    
    for student in students:
        student_data = {
            'student': student,
            'marks': {},
            'total_score': 0,
            'subject_count': 0
        }
        
        for subject in subjects:
            mark = Mark.query.filter_by(
                exam_id=exam_id,
                subject_id=subject.id,
                student_id=student.user_id
            ).first()
            
            score = mark.total if mark else 0
            student_data['marks'][subject.id] = score
            student_data['total_score'] += score
            student_data['subject_count'] += 1
            
        # Avoid division by zero
        count = student_data['subject_count'] if student_data['subject_count'] > 0 else 1
        percentage = student_data['total_score'] / count
        
        student_data['percentage'] = percentage
        student_data['grade'] = calculate_grade(percentage)
        student_data['gpa'] = calculate_gpa(percentage)
        
        results.append(student_data)
        
    # Class Statistics
    if not results:
        flash('No data found for this class.', 'warning')
        return redirect(url_for('marks.index'))

    # Topper
    topper = max(results, key=lambda x: x['total_score'])
    
    # Subject Highs
    subject_highs = {}
    for subject in subjects:
        high_score = 0
        scorer = None
        for r in results:
            s = r['marks'].get(subject.id, 0)
            if s > high_score:
                high_score = s
                scorer = r['student'].user.name
        subject_highs[subject.id] = {'score': high_score, 'scorer': scorer}
        
    # Class Average
    class_avg = sum(r['percentage'] for r in results) / len(results)
    
    return render_template('marks/class_results.html',
                         exam=exam,
                         my_class=my_class,
                         subjects=subjects,
                         results=results,
                         topper=topper,
                         subject_highs=subject_highs,
                         class_avg=class_avg)


@marks_bp.route('/result/<int:exam_id>/<int:student_id>')
@login_required
@teacher_or_admin_required
def student_result(exam_id, student_id):
    """Generate individual student result report"""
    exam = Exam.query.get_or_404(exam_id)
    student = User.query.get_or_404(student_id)
    
    # Get student record for class info associated with this student (current active session preferably)
    # Assuming the student record helps us identify the class.
    # We might need to handle cases where student has multiple records, but usually one active.
    # For now, we'll try to find the record matching the exam year or just the latest one.
    student_record = StudentRecord.query.filter_by(user_id=student_id).first()
    
    if not student_record:
        flash('Student record not found.', 'danger')
        return redirect(url_for('marks.index'))

    my_class = student_record.my_class
    subjects = Subject.query.filter_by(my_class_id=my_class.id).all()
    if not subjects:
        subjects = Subject.query.all()

    marks_data = []
    total_score = 0
    subject_count = 0
    
    for subject in subjects:
        mark = Mark.query.filter_by(
            exam_id=exam_id,
            subject_id=subject.id,
            student_id=student.id
        ).first()
        
        t1 = mark.t1 if mark else 0
        exams = mark.exams if mark else 0
        total = mark.total if mark else 0
        
        # Calculate grade for this specific subject
        # Note: Generic grading usually applies to the percentage of the subject score if max is 100
        # If max score is 100, score is percentage.
        grade = calculate_grade(total) 
        sub_remark = mark.teacher_remark if mark else ""
        
        marks_data.append({
            'subject': subject,
            't1': t1,
            'exams': exams,
            'total': total,
            'grade': grade,
            'remark': sub_remark
        })
        
        total_score += total
        subject_count += 1
        
    count = subject_count if subject_count > 0 else 1
    percentage = total_score / count
    overall_grade = calculate_grade(percentage)
    gpa = calculate_gpa(percentage)
    
    return render_template('marks/student_result.html',
                         exam=exam,
                         student=student,
                         student_record=student_record,
                         my_class=my_class,
                         marks_data=marks_data,
                         total_score=total_score,
                         percentage=percentage,
                         overall_grade=overall_grade,
                         gpa=gpa,
                         now=datetime.now)
