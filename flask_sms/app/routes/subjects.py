"""
Subjects management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Subject, MyClass, User, db
from app.forms.subject_forms import SubjectForm
from app.utils.helpers import admin_required

subjects_bp = Blueprint('subjects', __name__)


@subjects_bp.route('/')
@login_required
def index():
    """List all subjects"""
    subjects = Subject.query.all()
    return render_template('subjects/index.html', subjects=subjects)


@subjects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new subject"""
    form = SubjectForm()
    
    # Populate choices
    form.my_class_id.choices = [(c.id, c.name) for c in MyClass.query.all()]
    teachers = User.query.filter_by(user_type='teacher').all()
    form.teacher_id.choices = [(t.id, t.name) for t in teachers]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            slug=form.name.data.lower().replace(' ', '-'),
            my_class_id=form.my_class_id.data,
            teacher_id=form.teacher_id.data
        )
        db.session.add(subject)
        db.session.commit()
        
        flash(f'Subject {subject.name} created successfully!', 'success')
        return redirect(url_for('subjects.index'))
    
    return render_template('subjects/create.html', form=form)


@subjects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit subject"""
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    
    # Populate choices
    form.my_class_id.choices = [(c.id, c.name) for c in MyClass.query.all()]
    teachers = User.query.filter_by(user_type='teacher').all()
    form.teacher_id.choices = [(t.id, t.name) for t in teachers]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.my_class_id = form.my_class_id.data
        subject.teacher_id = form.teacher_id.data
        
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subjects.index'))
    
    return render_template('subjects/edit.html', form=form, subject=subject)


@subjects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete subject"""
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('subjects.index'))
