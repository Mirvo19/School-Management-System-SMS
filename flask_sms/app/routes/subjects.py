"""
Subjects management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import Subject, MyClass, User, db
from app.supabase_db import get_db, SupabaseModel
from app.forms.subject_forms import SubjectForm
from app.utils.helpers import admin_required

subjects_bp = Blueprint('subjects', __name__)


@subjects_bp.route('/')
@login_required
def index():
    """List all subjects"""
    supabase = get_db()
    res = supabase.table('subjects').select('*, my_class:my_classes(*), teacher:users(*)').execute()
    subjects = SupabaseModel.from_list(res.data)
    return render_template('subjects/index.html', subjects=subjects)


@subjects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new subject"""
    form = SubjectForm()
    supabase = get_db()
    
    # Populate choices
    res_c = supabase.table('my_classes').select('id, name').execute()
    form.my_class_id.choices = [(c['id'], c['name']) for c in res_c.data]
    
    res_t = supabase.table('users').select('id, name').eq('user_type', 'teacher').execute()
    form.teacher_id.choices = [(t['id'], t['name']) for t in res_t.data]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        new_subject = {
            'name': form.name.data,
            'slug': form.name.data.lower().replace(' ', '-'),
            'my_class_id': form.my_class_id.data,
            'teacher_id': form.teacher_id.data if form.teacher_id.data > 0 else None
        }
        
        try:
             supabase.table('subjects').insert(new_subject).execute()
             flash(f'Subject {form.name.data} created successfully!', 'success')
             return redirect(url_for('subjects.index'))
        except Exception as e:
             flash(f'Creation failed: {str(e)}', 'danger')
    
    return render_template('subjects/create.html', form=form)


@subjects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit subject"""
    supabase = get_db()
    res = supabase.table('subjects').select('*').eq('id', id).execute()
    if not res.data:
        abort(404)
        
    subject_data = res.data[0]
    subject = SupabaseModel(subject_data)
    form = SubjectForm(obj=subject)
    
    if request.method == 'GET':
        form.process(data=subject_data)
    
    # Populate choices
    res_c = supabase.table('my_classes').select('id, name').execute()
    form.my_class_id.choices = [(c['id'], c['name']) for c in res_c.data]
    
    res_t = supabase.table('users').select('id, name').eq('user_type', 'teacher').execute()
    form.teacher_id.choices = [(t['id'], t['name']) for t in res_t.data]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'my_class_id': form.my_class_id.data,
            'teacher_id': form.teacher_id.data if form.teacher_id.data > 0 else None
        }
        
        try:
            supabase.table('subjects').update(update_data).eq('id', id).execute()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('subjects.index'))
        except Exception as e:
            flash(f'Update failed: {str(e)}', 'danger')
    
    return render_template('subjects/edit.html', form=form, subject=subject)


@subjects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete subject"""
    supabase = get_db()
    try:
        supabase.table('subjects').delete().eq('id', id).execute()
        flash('Subject deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting subject: {str(e)}', 'danger')
        
    return redirect(url_for('subjects.index'))
