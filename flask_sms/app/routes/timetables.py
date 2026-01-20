"""
Timetables management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import TimeTable, TimeTableRecord, TimeSlot, MyClass, Subject, db
from app.utils.helpers import admin_required

timetables_bp = Blueprint('timetables', __name__)


@timetables_bp.route('/')
@login_required
def index():
    """List all timetables"""
    timetables = TimeTable.query.all()
    return render_template('timetables/index.html', timetables=timetables)


@timetables_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new timetable"""
    if request.method == 'POST':
        timetable = TimeTable(
            name=request.form.get('name'),
            my_class_id=request.form.get('my_class_id', type=int),
            year=request.form.get('year')
        )
        db.session.add(timetable)
        db.session.commit()
        
        flash('Timetable created successfully!', 'success')
        return redirect(url_for('timetables.show', id=timetable.id))
    
    classes = MyClass.query.all()
    return render_template('timetables/create.html', classes=classes)


@timetables_bp.route('/<int:id>')
@login_required
def show(id):
    """Show timetable"""
    timetable = TimeTable.query.get_or_404(id)
    records = TimeTableRecord.query.filter_by(tt_id=id).all()
    
    # Organize by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    schedule = {day: [] for day in days}
    
    for record in records:
        schedule[record.day].append(record)
    
    return render_template('timetables/show.html',
                         timetable=timetable,
                         schedule=schedule,
                         days=days)
