"""
Student management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, StudentRecord, MyClass, Section, Promotion, BloodGroup, State, Lga, Nationality, db
from app.forms.student_forms import StudentForm, PromotionForm
from app.utils.helpers import admin_required, teacher_or_admin_required
from sqlalchemy import or_

students_bp = Blueprint('students', __name__)


@students_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """List all students"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    students = StudentRecord.query.filter_by(grad=False, wd=False).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('students/index.html', students=students)


@students_bp.route('/list/<int:class_id>')
@login_required
@teacher_or_admin_required
def list_by_class(class_id):
    """List students by class"""
    my_class = MyClass.query.get_or_404(class_id)
    students = StudentRecord.query.filter_by(my_class_id=class_id, grad=False, wd=False).all()
    
    return render_template('students/list_by_class.html', students=students, my_class=my_class)


@students_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new student"""
    form = StudentForm()
    
    # Populate choices
    form.my_class_id.choices = [(c.id, c.name) for c in MyClass.query.all()]
    form.section_id.choices = [(s.id, s.name) for s in Section.query.filter_by(active=True).all()]
    form.my_parent_id.choices = [(p.id, p.name) for p in User.query.filter_by(user_type='parent').all()]
    form.my_parent_id.choices.insert(0, (0, 'Select Parent'))
    
    form.blood_group_id.choices = [(b.id, b.name) for b in BloodGroup.query.all()]
    form.blood_group_id.choices.insert(0, (0, 'Select Blood Group'))
    
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(f'Email {form.email.data} is already registered.', 'danger')
            return render_template('students/create.html', form=form)
            
        if User.query.filter_by(username=form.username.data).first():
            flash(f'Username {form.username.data} is already taken.', 'danger')
            return render_template('students/create.html', form=form)

        # Create user account
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            user_type='student',
            phone=form.phone.data,
            dob=form.dob.data,
            gender=form.gender.data,
            address=form.address.data,
            bg_id=form.blood_group_id.data if form.blood_group_id.data > 0 else None
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        # Create student record
        student_record = StudentRecord(
            user_id=user.id,
            my_class_id=form.my_class_id.data,
            section_id=form.section_id.data,
            my_parent_id=form.my_parent_id.data,
            adm_no=form.adm_no.data,
            year_admitted=form.year_admitted.data,
            session=form.session.data,
            house=form.house.data,
            age=form.age.data
        )
        db.session.add(student_record)
        db.session.commit()
        
        flash(f'Student {user.name} created successfully!', 'success')
        return redirect(url_for('students.index'))
    
    return render_template('students/create.html', form=form)


@students_bp.route('/<int:id>')
@login_required
def show(id):
    """Show student details"""
    student_record = StudentRecord.query.get_or_404(id)
    
    # Check permissions
    if not (current_user.is_admin() or current_user.is_teacher() or 
            current_user.id == student_record.user_id or 
            current_user.id == student_record.my_parent_id):
        flash('You do not have permission to view this student', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('students/show.html', student_record=student_record)


@students_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit student"""
    student_record = StudentRecord.query.get_or_404(id)
    user = student_record.user
    
    form = StudentForm(obj=user)
    
    # Populate choices
    form.my_class_id.choices = [(c.id, c.name) for c in MyClass.query.all()]
    form.section_id.choices = [(s.id, s.name) for s in Section.query.filter_by(active=True).all()]
    form.my_parent_id.choices = [(p.id, p.name) for p in User.query.filter_by(user_type='parent').all()]
    form.my_parent_id.choices.insert(0, (0, 'Select Parent'))
    
    form.blood_group_id.choices = [(b.id, b.name) for b in BloodGroup.query.all()]
    form.state_id.choices = [(s.id, s.name) for s in State.query.all()]
    form.lga_id.choices = [(l.id, l.name) for l in Lga.query.all()]
    form.nationality_id.choices = [(n.id, n.name) for n in Nationality.query.all()]
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.username = form.username.data
        user.phone = form.phone.data
        user.dob = form.dob.data
        user.gender = form.gender.data
        user.address = form.address.data
        
        student_record.my_class_id = form.my_class_id.data
        student_record.section_id = form.section_id.data
        student_record.my_parent_id = form.my_parent_id.data
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students.show', id=id))
    
    return render_template('students/edit.html', form=form, student_record=student_record)


@students_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete student"""
    student_record = StudentRecord.query.get_or_404(id)
    user = student_record.user
    
    db.session.delete(student_record)
    db.session.delete(user)
    db.session.commit()
    
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students.index'))


@students_bp.route('/graduated')
@login_required
@admin_required
def graduated():
    """List graduated students"""
    students = StudentRecord.query.filter_by(grad=True).all()
    return render_template('students/graduated.html', students=students)


@students_bp.route('/<int:id>/not-graduated', methods=['POST'])
@login_required
@admin_required
def not_graduated(id):
    """Mark student as not graduated"""
    student_record = StudentRecord.query.get_or_404(id)
    student_record.grad = False
    student_record.grad_date = None
    db.session.commit()
    
    flash('Student marked as not graduated', 'success')
    return redirect(url_for('students.graduated'))


@students_bp.route('/reset-pass/<int:st_id>', methods=['POST'])
@login_required
@admin_required
def reset_pass(st_id):
    """Reset student password"""
    student_record = StudentRecord.query.get_or_404(st_id)
    user = student_record.user
    
    # Reset to default password (e.g., student's admission number)
    user.set_password(student_record.adm_no)
    db.session.commit()
    
    flash(f'Password reset for {user.name}. New password: {student_record.adm_no}', 'success')
    return redirect(url_for('students.show', id=st_id))


@students_bp.route('/promotion', methods=['GET', 'POST'])
@login_required
@admin_required
def promotion():
    """Promote students"""
    if request.method == 'POST':
        from_class = request.form.get('from_class')
        from_section = request.form.get('from_section')
        to_class = request.form.get('to_class')
        to_section = request.form.get('to_section')
        from_session = request.form.get('from_session')
        to_session = request.form.get('to_session')
        
        return redirect(url_for('students.promotion_selector',
                              fc=from_class, fs=from_section,
                              tc=to_class, ts=to_section,
                              from_session=from_session, to_session=to_session))
    
    classes = MyClass.query.all()
    return render_template('students/promotion.html', classes=classes)


@students_bp.route('/promotion/selector')
@login_required
@admin_required
def promotion_selector():
    """Select students for promotion"""
    fc = request.args.get('fc', type=int)
    fs = request.args.get('fs', type=int)
    tc = request.args.get('tc', type=int)
    ts = request.args.get('ts', type=int)
    from_session = request.args.get('from_session')
    to_session = request.args.get('to_session')
    
    students = StudentRecord.query.filter_by(
        my_class_id=fc, section_id=fs, session=from_session
    ).all()
    
    from_class = MyClass.query.get(fc)
    to_class = MyClass.query.get(tc)
    
    return render_template('students/promotion_selector.html',
                         students=students, from_class=from_class,
                         to_class=to_class, tc=tc, ts=ts,
                         from_session=from_session, to_session=to_session)


@students_bp.route('/promotion/promote', methods=['POST'])
@login_required
@admin_required
def promote():
    """Execute student promotion"""
    student_ids = request.form.getlist('student_ids[]')
    to_class = request.form.get('to_class', type=int)
    to_section = request.form.get('to_section', type=int)
    to_session = request.form.get('to_session')
    
    for student_id in student_ids:
        student_record = StudentRecord.query.get(student_id)
        if student_record:
            # Create promotion record
            promotion = Promotion(
                student_id=student_record.user_id,
                from_class=student_record.my_class_id,
                from_section=student_record.section_id,
                to_class=to_class,
                to_section=to_section,
                from_session=student_record.session,
                to_session=to_session
            )
            db.session.add(promotion)
            
            # Update student record
            student_record.my_class_id = to_class
            student_record.section_id = to_section
            student_record.session = to_session
    
    db.session.commit()
    flash(f'{len(student_ids)} students promoted successfully!', 'success')
    return redirect(url_for('students.index'))


@students_bp.route('/promotion/manage')
@login_required
@admin_required
def promotion_manage():
    """Manage promotions"""
    promotions = Promotion.query.order_by(Promotion.created_at.desc()).all()
    return render_template('students/promotion_manage.html', promotions=promotions)


@students_bp.route('/promotion/reset/<int:pid>', methods=['POST'])
@login_required
@admin_required
def promotion_reset(pid):
    """Reset a promotion"""
    promotion = Promotion.query.get_or_404(pid)
    student_record = StudentRecord.query.filter_by(user_id=promotion.student_id).first()
    
    if student_record:
        student_record.my_class_id = promotion.from_class
        student_record.section_id = promotion.from_section
        student_record.session = promotion.from_session
    
    db.session.delete(promotion)
    db.session.commit()
    
    flash('Promotion reset successfully!', 'success')
    return redirect(url_for('students.promotion_manage'))
