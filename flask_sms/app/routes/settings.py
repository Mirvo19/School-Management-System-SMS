"""
Settings management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Setting, db
from app.utils.helpers import admin_required

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
@admin_required
def index():
    """System settings"""
    settings = Setting.query.all()
    return render_template('settings/index.html', settings=settings)
