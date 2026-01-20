"""
Dormitories management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Dorm, db
from app.utils.helpers import admin_required

dorms_bp = Blueprint('dorms', __name__)


@dorms_bp.route('/')
@login_required
def index():
    """List all dormitories"""
    dorms = Dorm.query.all()
    return render_template('dorms/index.html', dorms=dorms)


@dorms_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new dormitory"""
    if request.method == 'POST':
        dorm = Dorm(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(dorm)
        db.session.commit()
        
        flash('Dormitory created successfully!', 'success')
        return redirect(url_for('dorms.index'))
    
    return render_template('dorms/create.html')
