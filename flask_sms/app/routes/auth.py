"""
Authentication routes - Login, Logout, Register
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# from app.models import User, db
from app.supabase_db import get_db, SupabaseModel
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms.auth_forms import LoginForm, RegisterForm, ChangePasswordForm
from werkzeug.urls import url_parse

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Supabase Login Logic
        identity = form.identity.data
        
        try:
            supabase = get_db()
            
            # Or query: email = identity OR username = identity
            # Note: Supabase-py doesn't support sophisticated OR queries easily in one go 
            # without calling .or_(). Let's try matching email first, then username.
            
            # Try finding by email
            response = supabase.table('users').select('*').eq('email', identity).execute()
            data = response.data
            
            # If not found, try username
            if not data:
                response = supabase.table('users').select('*').eq('username', identity).execute()
                data = response.data
        except Exception as e:
            flash(f"System Error: Cannot connect to authentication service. ({str(e)})", 'danger')
            return render_template('auth/login.html', form=form)

        if data:
            user_data = data[0] # Get first result
            if check_password_hash(user_data['password'], form.password.data):
                user_obj = SupabaseModel(user_data)
                login_user(user_obj, remember=form.remember_me.data)
                
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('main.dashboard')
                flash('Login successful!', 'success')
                return redirect(next_page)
            else:
                 flash('Invalid username/email or password', 'danger')
        else:
            flash('Invalid username/email or password', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (if enabled)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        supabase = get_db()
        
        # Check if email/username exists
        # This is a bit manual without constraints catching errors gracefully
        
        # Create user dict
        new_user = {
            'name': form.name.data,
            'email': form.email.data,
            'username': form.username.data,
            'user_type': 'student',
            'password': generate_password_hash(form.password.data)
        }
        
        try:
             response = supabase.table('users').insert(new_user).execute()
             flash('Registration successful! Please login.', 'success')
             return redirect(url_for('auth.login'))
        except Exception as e:
             # Handle unique violation etc (typically Supabase returns an error structure)
             flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)
