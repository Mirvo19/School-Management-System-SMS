"""
Helper functions and decorators
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check for super_admin OR admin
        if not (current_user.user_type == 'super_admin' or current_user.user_type == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def accountant_required(f):
    """Decorator to require accountant access (or admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        allowed_types = ['super_admin', 'admin', 'accountant']
        if current_user.user_type not in allowed_types:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function



def teacher_required(f):
    """Decorator to require teacher access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_teacher():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def teacher_or_admin_required(f):
    """Decorator to require teacher or admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not (current_user.is_teacher() or current_user.is_admin()):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to require student access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_student():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def format_date(date_obj, format='%Y-%m-%d'):
    """Format date object"""
    if date_obj:
        return date_obj.strftime(format)
    return ''


def get_current_session():
    """Get current academic session"""
    from datetime import datetime
    year = datetime.now().year
    return f'{year}/{year + 1}'


def calculate_age(dob):
    """Calculate age from date of birth"""
    from datetime import datetime
    if dob:
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return None
