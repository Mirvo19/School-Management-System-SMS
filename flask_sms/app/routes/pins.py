"""
PINs management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Pin, db
from app.utils.helpers import admin_required
import secrets

pins_bp = Blueprint('pins', __name__)


@pins_bp.route('/')
@login_required
@admin_required
def index():
    """List all PINs"""
    pins = Pin.query.order_by(Pin.created_at.desc()).all()
    return render_template('pins/index.html', pins=pins)


@pins_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Generate new PINs"""
    if request.method == 'POST':
        count = request.form.get('count', type=int, default=1)
        
        for _ in range(count):
            code = secrets.token_hex(8).upper()
            pin = Pin(code=code)
            db.session.add(pin)
        
        db.session.commit()
        flash(f'{count} PIN(s) generated successfully!', 'success')
        return redirect(url_for('pins.index'))
    
    return render_template('pins/create.html')
