"""
Timetables management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import TimeTable, TimeTableRecord, TimeSlot, MyClass, Subject, db
from app.supabase_db import get_db, SupabaseModel
from app.utils.helpers import admin_required

timetables_bp = Blueprint('timetables', __name__)


@timetables_bp.route('/')
@login_required
def index():
    """List all timetables"""
    supabase = get_db()
    res = supabase.table('timetables').select('*, my_class:my_classes(*)').execute()
    timetables = SupabaseModel.from_list(res.data)
    return render_template('timetables/index.html', timetables=timetables)


@timetables_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new timetable"""
    supabase = get_db()
    
    if request.method == 'POST':
        new_tt = {
            'name': request.form.get('name'),
            'my_class_id': request.form.get('my_class_id', type=int),
            'year': request.form.get('year')
        }
        try:
            res = supabase.table('timetables').insert(new_tt).execute()
            new_id = res.data[0]['id']
            flash('Timetable created successfully!', 'success')
            return redirect(url_for('timetables.show', id=new_id))
        except Exception as e:
            flash(f'Creation failed: {str(e)}', 'danger')
    
    res_c = supabase.table('my_classes').select('*').execute()
    classes = SupabaseModel.from_list(res_c.data)
    return render_template('timetables/create.html', classes=classes)


@timetables_bp.route('/<int:id>')
@login_required
def show(id):
    """Show timetable"""
    supabase = get_db()
    
    # Get Timetable
    res_tt = supabase.table('timetables').select('*, my_class:my_classes(*)').eq('id', id).execute()
    if not res_tt.data:
        abort(404)
    timetable = SupabaseModel(res_tt.data[0])
    
    # Get Records
    # Join subject and time_slot (if exists) usually subject name is needed
    res_rec = supabase.table('timetable_records').select('*, subject:subjects(*)').eq('tt_id', id).execute()
    records = SupabaseModel.from_list(res_rec.data)
    
    # Organize by day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    schedule = {day: [] for day in days}
    
    for record in records:
        # Assuming record has 'day' field
        if record.day in schedule:
            schedule[record.day].append(record)
    
    # Sort records by time? Assuming start_time is present or order by ID
    
    return render_template('timetables/show.html',
                         timetable=timetable,
                         schedule=schedule,
                         days=days)
