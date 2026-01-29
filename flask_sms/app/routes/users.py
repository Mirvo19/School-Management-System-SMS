"""
User management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.supabase_db import get_db, SupabaseModel
from datetime import datetime
# from app.models import User, StaffRecord, db
from app.forms.user_forms import UserForm, StaffForm
from werkzeug.security import generate_password_hash
from app.utils.helpers import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@login_required
@admin_required
def index():
    """List all users"""
    user_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page - 1
    
    supabase = get_db()
    query = supabase.table('users').select('*', count='exact')
    
    if user_type != 'all':
        query = query.eq('user_type', user_type)
    
    # Range is 0-indexed and inclusive in Supabase
    res = query.range(start, end).execute()
    total_count = res.count
    
    # Create a wrapper object to mimic Flask-SQLAlchemy pagination object
    class PaginationMock:
        def __init__(self, items, page, per_page, total):
            self.items = SupabaseModel.from_list(items)
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
            
        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
             # Simplified iteration logic
             last = 0
             for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and \
                    num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    users = PaginationMock(res.data, page, per_page, total_count)
    
    return render_template('users/index.html', users=users, user_type=user_type)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new user"""
    form = UserForm()
    supabase = get_db()
    
    if form.validate_on_submit():
        # Duplicate checks
        res_email = supabase.table('users').select('id').eq('email', form.email.data).execute()
        if res_email.data:
            flash(f'Email {form.email.data} is already registered.', 'danger')
            return render_template('users/create.html', form=form)
            
        res_user = supabase.table('users').select('id').eq('username', form.username.data).execute()
        if res_user.data:
            flash(f'Username {form.username.data} is already taken.', 'danger')
            return render_template('users/create.html', form=form)

        # Basic Fields
        new_user = {
            'name': form.name.data,
            'email': form.email.data,
            'username': form.username.data,
            'user_type': form.user_type.data,
            'phone': form.phone.data,
            'dob': str(form.dob.data) if form.dob.data else None,
            'gender': form.gender.data,
            'address': form.address.data,
            'password': generate_password_hash(form.password.data)
        }
        
        try:
             supabase.table('users').insert(new_user).execute()
             flash(f'User {form.name.data} created successfully!', 'success')
             return redirect(url_for('users.index'))
        except Exception as e:
             flash(f'Creation failed: {str(e)}', 'danger')
    
    return render_template('users/create.html', form=form)


@users_bp.route('/<int:id>')
@login_required
def show(id):
    """Show user details"""
    supabase = get_db()
    res = supabase.table('users').select('*').eq('id', id).execute()
    if not res.data:
        flash('User not found', 'danger')
        return redirect(url_for('users.index'))
        
    if not res.data:
        flash('User not found', 'danger')
        return redirect(url_for('users.index'))
        
    user = SupabaseModel(res.data[0])
    
    # Fix date formatting for show view
    if user.created_at and isinstance(user.created_at, str):
        try:
             user.created_at = datetime.fromisoformat(user.created_at.replace('Z', '+00:00'))
        except: pass

    if user.dob and isinstance(user.dob, str):
        try:
             # Handle simple date string "YYYY-MM-DD" or full ISO timestamp
             dob_str = str(user.dob).split('T')[0]
             user.dob = datetime.strptime(dob_str, '%Y-%m-%d')
        except: pass
        
    return render_template('users/show.html', user=user)


@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit user"""
    supabase = get_db()
    res = supabase.table('users').select('*').eq('id', id).execute()
    if not res.data:
         flash('User not found', 'danger')
         return redirect(url_for('users.index'))
    
    user_data = res.data[0]
    user = SupabaseModel(user_data)
    form = UserForm(obj=user)
    
    if request.method == 'GET':
        # FIX: WTForms DateField requires a date object, not a string
        if user_data.get('dob'):
            try:
                # Handle cases where dob might be full datetime string from DB or simple date
                dob_str = str(user_data['dob']).split('T')[0]
                user_data['dob'] = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except Exception as e:
                print(f"Error parsing date: {e}")
        
        form.process(data=user_data) # Populate form from dict
    
    if form.validate_on_submit():
        update_data = {
           'name': form.name.data,
           'email': form.email.data,
           'username': form.username.data,
           'user_type': form.user_type.data,
           'phone': form.phone.data,
           'dob': str(form.dob.data) if form.dob.data else None,
           'gender': form.gender.data,
           'address': form.address.data
        }
        
        try:
             supabase.table('users').update(update_data).eq('id', id).execute()
             flash('User updated successfully!', 'success')
             return redirect(url_for('users.show', id=id))
        except Exception as e:
             flash(f'Update failed: {str(e)}', 'danger')
    
    return render_template('users/edit.html', form=form, user=user)


@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete user"""
    supabase = get_db()
    try:
        supabase.table('users').delete().eq('id', id).execute()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
        
    return redirect(url_for('users.index'))


@users_bp.route('/reset-pass/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_pass(id):
    """Reset user password with custom value"""
    supabase = get_db()
    res = supabase.table('users').select('*').eq('id', id).execute()
    if not res.data:
        return redirect(url_for('users.index'))
    user = SupabaseModel(res.data[0])
    
    if request.method == 'POST':
        password = request.form.get('password')
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
        else:
            new_hash = generate_password_hash(password)
            supabase.table('users').update({'password': new_hash}).eq('id', id).execute()
            flash(f'Password changed successfully for {user.name}.', 'success')
            return redirect(url_for('users.show', id=id))
            
    return render_template('users/reset_pass.html', user=user)
