"""
Exams management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import Exam, ExamRecord, db
from app.supabase_db import get_db, SupabaseModel
from app.forms.exam_forms import ExamForm
from app.utils.helpers import admin_required, teacher_or_admin_required

exams_bp = Blueprint('exams', __name__)


@exams_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """List all exams"""
    supabase = get_db()
    res = supabase.table('exams').select('*').order('year', desc=True).order('term', desc=True).execute()
    exams = SupabaseModel.from_list(res.data)
    return render_template('exams/index.html', exams=exams)


@exams_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new exam"""
    form = ExamForm()
    supabase = get_db()
    
    if form.validate_on_submit():
        new_exam = {
            'name': form.name.data,
            'year': form.year.data,
            'term': form.term.data
        }
        try:
             supabase.table('exams').insert(new_exam).execute()
             flash(f'Exam {form.name.data} created successfully!', 'success')
             return redirect(url_for('exams.index'))
        except Exception as e:
             flash(f'Creation failed: {str(e)}', 'danger')
    
    return render_template('exams/create.html', form=form)


@exams_bp.route('/<int:id>')
@login_required
@teacher_or_admin_required
def show(id):
    """Show exam details"""
    supabase = get_db()
    
    # Get Exam
    res_exam = supabase.table('exams').select('*').eq('id', id).execute()
    if not res_exam.data:
        abort(404)
    exam = SupabaseModel(res_exam.data[0])
    
    # Get Exam Records (might need detailed join)
    # exam_records (*, student:users(*), my_class:my_classes(*), section:sections(*))
    res_rec = supabase.table('exam_records').select(
        '*, student:users(*), my_class:my_classes(*), section:sections(*)'
    ).eq('exam_id', id).execute()
    
    exam_records = SupabaseModel.from_list(res_rec.data)
    
    return render_template('exams/show.html', exam=exam, exam_records=exam_records)
