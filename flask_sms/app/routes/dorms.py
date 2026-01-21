"""
Dormitories management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
# from app.models import Dorm, db
from app.supabase_db import get_db, SupabaseModel
from app.utils.helpers import admin_required

dorms_bp = Blueprint('dorms', __name__)


@dorms_bp.route('/')
@login_required
def index():
    """List all dormitories"""
    supabase = get_db()
    res = supabase.table('dorms').select('*').execute()
    dorms = SupabaseModel.from_list(res.data)
    return render_template('dorms/index.html', dorms=dorms)


@dorms_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new dormitory"""
    supabase = get_db()
    
    if request.method == 'POST':
        new_dorm = {
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        try:
            supabase.table('dorms').insert(new_dorm).execute()
            flash('Dormitory created successfully!', 'success')
            return redirect(url_for('dorms.index'))
        except Exception as e:
            flash(f'Creation failed: {str(e)}', 'danger')
    
    return render_template('dorms/create.html')
