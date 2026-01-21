"""
PINs management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
# from app.models import Pin, db
from app.supabase_db import get_db, SupabaseModel
from app.utils.helpers import admin_required
import secrets

pins_bp = Blueprint('pins', __name__)


@pins_bp.route('/')
@login_required
@admin_required
def index():
    """List all PINs"""
    supabase = get_db()
    res = supabase.table('pins').select('*').order('created_at', desc=True).execute()
    pins = SupabaseModel.from_list(res.data)
    return render_template('pins/index.html', pins=pins)


@pins_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Generate new PINs"""
    if request.method == 'POST':
        count = request.form.get('count', type=int, default=1)
        supabase = get_db()
        
        pins_data = []
        for _ in range(count):
            code = secrets.token_hex(8).upper()
            pins_data.append({'code': code})
        
        try:
            supabase.table('pins').insert(pins_data).execute()
            flash(f'{count} PIN(s) generated successfully!', 'success')
            return redirect(url_for('pins.index'))
        except Exception as e:
            flash(f'Pin generation failed: {str(e)}', 'danger')
    
    return render_template('pins/create.html')
