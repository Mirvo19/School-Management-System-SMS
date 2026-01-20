"""
User management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import User, StaffRecord, db
from app.forms.user_forms import UserForm, StaffForm
from app.utils.helpers import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@admin_required
def index():
    """List all users"""
    user_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    if user_type != 'all':
        query = query.filter_by(user_type=user_type)
    
    users = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('users/index.html', users=users, user_type=user_type)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new user"""
    form = UserForm()
    
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(f'Email {form.email.data} is already registered.', 'danger')
            return render_template('users/create.html', form=form)
            
        if User.query.filter_by(username=form.username.data).first():
            flash(f'Username {form.username.data} is already taken.', 'danger')
            return render_template('users/create.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            user_type=form.user_type.data,
            phone=form.phone.data,
            dob=form.dob.data,
            gender=form.gender.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.name} created successfully!', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/create.html', form=form)


@users_bp.route('/<int:id>')
@login_required
def show(id):
    """Show user details"""
    user = User.query.get_or_404(id)
    return render_template('users/show.html', user=user)


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit user"""
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.username = form.username.data
        user.user_type = form.user_type.data
        user.phone = form.phone.data
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.show', id=id))
    
    return render_template('users/edit.html', form=form, user=user)


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete user"""
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/reset-pass/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_pass(id):
    """Reset user password with custom value"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        password = request.form.get('password')
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
        else:
            user.set_password(password)
            db.session.commit()
            flash(f'Password changed successfully for {user.name}.', 'success')
            return redirect(url_for('users.show', id=id))
            
    return render_template('users/reset_pass.html', user=user)
