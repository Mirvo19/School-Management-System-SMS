"""
Classes and sections management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import MyClass, Section, ClassType, db, User
from app.forms.class_forms import ClassForm, SectionForm
from app.utils.helpers import admin_required

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('/')
@login_required
def index():
    """List all classes"""
    classes = MyClass.query.all()
    return render_template('classes/index.html', classes=classes)


@classes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new class"""
    form = ClassForm()
    
    if form.validate_on_submit():
        my_class = MyClass(
            name=form.name.data,
            class_type_id=form.class_type_id.data
        )
        db.session.add(my_class)
        db.session.commit()
        
        flash(f'Class {my_class.name} created successfully!', 'success')
        return redirect(url_for('classes.index'))
    
    return render_template('classes/create.html', form=form)


@classes_bp.route('/<int:id>')
@login_required
def show(id):
    """Show class details"""
    my_class = MyClass.query.get_or_404(id)
    sections = Section.query.filter_by(my_class_id=id).all()
    return render_template('classes/show.html', my_class=my_class, sections=sections)


@classes_bp.route('/<int:id>/sections/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_section(id):
    """Create section for a class"""
    my_class = MyClass.query.get_or_404(id)
    form = SectionForm()
    
    # Populate teacher choices
    teachers = User.query.filter_by(user_type='teacher').all()
    form.teacher_id.choices = [(t.id, t.name) for t in teachers]
    form.teacher_id.choices.insert(0, (0, 'Select Teacher'))
    
    if form.validate_on_submit():
        section = Section(
            name=form.name.data,
            my_class_id=id,
            teacher_id=form.teacher_id.data,
            active=form.active.data
        )
        db.session.add(section)
        db.session.commit()
        
        flash(f'Section {section.name} created successfully!', 'success')
        return redirect(url_for('classes.show', id=id))
    
    return render_template('classes/create_section.html', form=form, my_class=my_class)
