"""
Classes and sections management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import MyClass, Section, ClassType, db, User
from app.supabase_db import get_db, SupabaseModel
from datetime import datetime
from app.forms.class_forms import ClassForm, SectionForm
from app.utils.helpers import admin_required

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('/')
@login_required
def index():
    """List all classes"""
    supabase = get_db()
    # Join with class_type to get type info if needed, usually needed for display
    res = supabase.table('my_classes').select('*, class_type:class_types(*)').execute()
    classes = SupabaseModel.from_list(res.data)
    
    # Fix date formatting
    for c in classes:
        if c.created_at and isinstance(c.created_at, str):
            try:
                c.created_at = datetime.fromisoformat(c.created_at.replace('Z', '+00:00'))
            except: pass

    return render_template('classes/index.html', classes=classes)


@classes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new class"""
    form = ClassForm()
    supabase = get_db()
    
    # Populate Class Types choice dynamically if needed, 
    # but currently form might handle it statically or we need to add logic here if ClassForm selects from DB
    res_ct = supabase.table('class_types').select('id, name').execute()
    form.class_type_id.choices = [(c['id'], c['name']) for c in res_ct.data]

    if form.validate_on_submit():
        new_class = {
            'name': form.name.data,
            'class_type_id': form.class_type_id.data
        }
        try:
            supabase.table('my_classes').insert(new_class).execute()
            flash(f'Class {form.name.data} created successfully!', 'success')
            return redirect(url_for('classes.index'))
        except Exception as e:
            flash(f'Error creating class: {str(e)}', 'danger')
    
    return render_template('classes/create.html', form=form)


@classes_bp.route('/<int:id>')
@login_required
def show(id):
    """Show class details"""
    supabase = get_db()
    
    # Get Class
    res_cls = supabase.table('my_classes').select('*, class_type:class_types(*)').eq('id', id).execute()
    if not res_cls.data:
        abort(404)
        
    my_class = SupabaseModel(res_cls.data[0])
    
    # Get Sections
    # Join teacher info
    res_sec = supabase.table('sections').select('*, teacher:users(*)').eq('my_class_id', id).execute()
    sections = SupabaseModel.from_list(res_sec.data)
    
    return render_template('classes/show.html', my_class=my_class, sections=sections)


@classes_bp.route('/<int:id>/sections/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_section(id):
    """Create section for a class"""
    supabase = get_db()
    res_cls = supabase.table('my_classes').select('*').eq('id', id).execute()
    if not res_cls.data:
        abort(404)
    my_class = SupabaseModel(res_cls.data[0])
    
    form = SectionForm()
    
    # Populate teacher choices
    res_t = supabase.table('users').select('id, name').eq('user_type', 'teacher').execute()
    form.teacher_id.choices = [(t['id'], t['name']) for t in res_t.data]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        new_section = {
            'name': form.name.data,
            'my_class_id': id,
            'teacher_id': form.teacher_id.data if form.teacher_id.data > 0 else None,
            'active': form.active.data
        }
        
        try:
            supabase.table('sections').insert(new_section).execute()
            flash(f'Section {form.name.data} created successfully!', 'success')
            return redirect(url_for('classes.show', id=id))
        except Exception as e:
            flash(f'Error creating section: {str(e)}', 'danger')
    
    return render_template('classes/create_section.html', form=form, my_class=my_class)
