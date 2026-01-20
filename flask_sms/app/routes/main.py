"""
Main routes - Dashboard, Home, Profile
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, StudentRecord, StaffRecord, db
from app.forms.profile_forms import ProfileForm, ChangePasswordForm
from app.utils.helpers import admin_required, teacher_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    context = {
        'user': current_user
    }
    
    if current_user.is_admin():
        # Admin dashboard statistics
        context['total_students'] = User.query.filter_by(user_type='student').count()
        context['total_teachers'] = User.query.filter_by(user_type='teacher').count()
        context['total_parents'] = User.query.filter_by(user_type='parent').count()
        return render_template('dashboard/admin.html', **context)
    
    elif current_user.is_teacher():
        # Teacher dashboard
        return render_template('dashboard/teacher.html', **context)
    
    elif current_user.is_student():
        # Student dashboard
        student_record = StudentRecord.query.filter_by(user_id=current_user.id).first()
        context['student_record'] = student_record
        return render_template('dashboard/student.html', **context)
    
    elif current_user.is_parent():
        # Parent dashboard
        children = StudentRecord.query.filter_by(my_parent_id=current_user.id).all()
        context['children'] = children
        return render_template('dashboard/parent.html', **context)
    
    elif current_user.user_type == 'accountant':
        # Accountant dashboard
        return render_template('dashboard/accountant.html', **context)
    
    return render_template('dashboard/default.html', **context)


@main_bp.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    """Edit user profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.phone2 = form.phone2.data
        current_user.address = form.address.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.my_account'))
    
    return render_template('main/profile.html', form=form)


@main_bp.route('/my-account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('main.my_account'))
        else:
            flash('Current password is incorrect', 'danger')
    
    return render_template('main/change_password.html', form=form)


@main_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page"""
    return render_template('main/privacy_policy.html')


@main_bp.route('/terms-of-use')
def terms_of_use():
    """Terms of use page"""
    return render_template('main/terms_of_use.html')
