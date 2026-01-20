"""
Exams management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Exam, ExamRecord, db
from app.forms.exam_forms import ExamForm
from app.utils.helpers import admin_required, teacher_or_admin_required

exams_bp = Blueprint('exams', __name__)


@exams_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """List all exams"""
    exams = Exam.query.order_by(Exam.year.desc(), Exam.term.desc()).all()
    return render_template('exams/index.html', exams=exams)


@exams_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new exam"""
    form = ExamForm()
    
    if form.validate_on_submit():
        exam = Exam(
            name=form.name.data,
            year=form.year.data,
            term=form.term.data
        )
        db.session.add(exam)
        db.session.commit()
        
        flash(f'Exam {exam.name} created successfully!', 'success')
        return redirect(url_for('exams.index'))
    
    return render_template('exams/create.html', form=form)


@exams_bp.route('/<int:id>')
@login_required
@teacher_or_admin_required
def show(id):
    """Show exam details"""
    exam = Exam.query.get_or_404(id)
    exam_records = ExamRecord.query.filter_by(exam_id=id).all()
    return render_template('exams/show.html', exam=exam, exam_records=exam_records)
