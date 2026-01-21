"""
Settings management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
# from app.models import Setting, db
from app.supabase_db import get_db, SupabaseModel
from app.utils.helpers import admin_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
@admin_required
def index():
    """System settings"""
    supabase = get_db()
    res = supabase.table('settings').select('*').execute()
    settings = SupabaseModel.from_list(res.data)
    return render_template('settings/index.html', settings=settings)
