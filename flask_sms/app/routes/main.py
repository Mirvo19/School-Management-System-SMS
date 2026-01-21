"""
Main routes - Dashboard, Home, Profile
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.supabase_db import get_db, SupabaseModel
# from app.models import User, StudentRecord, StaffRecord, db
from app.forms.profile_forms import ProfileForm, ChangePasswordForm
from app.utils.helpers import admin_required, teacher_required
from werkzeug.security import check_password_hash, generate_password_hash

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
    supabase = get_db()
    
    # We need to wrap current_user properly or access its dict
    # current_user is already a SupabaseModel thanks to load_user
    
    context = {
        'user': current_user
    }
    
    user_type = current_user.get('user_type')
    
    if user_type == 'super_admin' or user_type == 'admin':
        # Admin dashboard statistics
        # Note: count() in supabase-py might need 'exact' param or similar depending on version
        # .select('*', count='exact').eq(...) is standard way
        
        try:
           res_st = supabase.table('users').select('*', count='exact').eq('user_type', 'student').execute()
           context['total_students'] = res_st.count
           
           res_te = supabase.table('users').select('*', count='exact').eq('user_type', 'teacher').execute()
           context['total_teachers'] = res_te.count
           
           res_pa = supabase.table('users').select('*', count='exact').eq('user_type', 'parent').execute()
           context['total_parents'] = res_pa.count
        except:
           context['total_students'] = 0
           context['total_teachers'] = 0
           context['total_parents'] = 0
           
        return render_template('dashboard/admin.html', **context)
    
    elif user_type == 'teacher':
        # Teacher dashboard
        return render_template('dashboard/teacher.html', **context)
    
    elif user_type == 'student':
        # Student dashboard
        # student_record = StudentRecord.query.filter_by(user_id=current_user.id).first()
        res = supabase.table('student_records').select('*').eq('user_id', current_user.get('id')).execute()
        student_record = SupabaseModel(res.data[0]) if res.data else None
        
        context['student_record'] = student_record
        return render_template('dashboard/student.html', **context)
    
    elif user_type == 'parent':
        # Parent dashboard
        # children = StudentRecord.query.filter_by(my_parent_id=current_user.id).all()
        res = supabase.table('student_records').select('*').eq('my_parent_id', current_user.get('id')).execute()
        children = SupabaseModel.from_list(res.data) if res.data else []
        
        context['children'] = children
        return render_template('dashboard/parent.html', **context)
    
    elif user_type == 'accountant':
        # Accountant dashboard
        return render_template('dashboard/accountant.html', **context)
    
    return render_template('dashboard/default.html', **context)


@main_bp.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    """Edit user profile"""
    # Create fake object for form population since current_user is SupabaseModel (read-only-ish)
    # Actually SupabaseModel has get(), so obj=current_user might fail if form expects object attributes
    # But we added __getattr__ logic via SupabaseModel constructor iterating dict. 
    # Let's hope WTForms works with it or we might need a dict to obj adapter.
    # We already did that in SupabaseModel(data) -> setattr.
    
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        supabase = get_db()
        update_data = {
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'phone2': form.phone2.data,
            'address': form.address.data
        }
        
        try:
            supabase.table('users').update(update_data).eq('id', current_user.get('id')).execute()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.my_account'))
        except Exception as e:
            flash(f'Update failed: {str(e)}', 'danger')
    
    return render_template('main/profile.html', form=form)


@main_bp.route('/my-account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password
        # current_user has 'password' hash in it? Yes from load_user
        if check_password_hash(current_user.get('password'), form.current_password.data):
             new_hash = generate_password_hash(form.new_password.data)
             supabase = get_db()
             try:
                 supabase.table('users').update({'password': new_hash}).eq('id', current_user.get('id')).execute()
                 flash('Password changed successfully!', 'success')
                 return redirect(url_for('main.my_account'))
             except Exception as e:
                 flash('Error updating password', 'danger')
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
