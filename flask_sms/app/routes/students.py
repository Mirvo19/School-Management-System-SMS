"""
Student management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
# from app.models import User, StudentRecord, MyClass, Section, Promotion, BloodGroup, State, Lga, Nationality, db
from app.supabase_db import get_db, SupabaseModel
from werkzeug.security import generate_password_hash
from app.forms.student_forms import StudentForm, PromotionForm
from app.utils.helpers import admin_required, teacher_or_admin_required
# from sqlalchemy import or_

students_bp = Blueprint('students', __name__)


@students_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """List all students"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page - 1
    
    supabase = get_db()
    # Fetch students with user info. Supabase join syntax:
    # student_records (*, user:user_id (*), my_class:my_class_id (*), section:section_id (*))
    
    res = supabase.table('student_records').select(
        '*, user:users(*), my_class:my_classes(*), section:sections(*)', count='exact'
    ).eq('grad', False).eq('wd', False).range(start, end).execute()
    
    total_count = res.count
    
    # Create a wrapper object to mimic Flask-SQLAlchemy pagination object
    class PaginationMock:
        def __init__(self, items, page, per_page, total):
            self.items = SupabaseModel.from_list(items)
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1
            
        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
             last = 0
             for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and \
                    num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    students = PaginationMock(res.data, page, per_page, total_count)
    
    return render_template('students/index.html', students=students)


@students_bp.route('/list/<int:class_id>')
@login_required
@teacher_or_admin_required
def list_by_class(class_id):
    """List students by class"""
    supabase = get_db()
    
    # Get Class Name
    res_cls = supabase.table('my_classes').select('*').eq('id', class_id).execute()
    my_class = SupabaseModel(res_cls.data[0]) if res_cls.data else None
    
    if not my_class:
        flash('Class not found', 'danger')
        return redirect(url_for('students.index'))
    
    # Get Students
    res = supabase.table('student_records').select(
         '*, user:users(*), my_class:my_classes(*), section:sections(*)'
    ).eq('my_class_id', class_id).eq('grad', False).eq('wd', False).execute()
    
    students = SupabaseModel.from_list(res.data)
    
    return render_template('students/list_by_class.html', students=students, my_class=my_class)


@students_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create new student"""
    form = StudentForm()
    supabase = get_db()
    
    # Populate choices
    res_c = supabase.table('my_classes').select('id, name').execute()
    form.my_class_id.choices = [(c['id'], c['name']) for c in res_c.data]
    
    res_s = supabase.table('sections').select('id, name').eq('active', True).execute()
    form.section_id.choices = [(s['id'], s['name']) for s in res_s.data]
    
    res_p = supabase.table('users').select('id, name').eq('user_type', 'parent').execute()
    form.my_parent_id.choices = [(p['id'], p['name']) for p in res_p.data]
    form.my_parent_id.choices.insert(0, (0, 'Select Parent'))
    
    res_bg = supabase.table('blood_groups').select('id, name').execute()
    form.blood_group_id.choices = [(b['id'], b['name']) for b in res_bg.data]
    form.blood_group_id.choices.insert(0, (0, 'Select Blood Group'))
    
    if form.validate_on_submit():
        # Check Existing
        res_email = supabase.table('users').select('id').eq('email', form.email.data).execute()
        if res_email.data:
            flash(f'Email {form.email.data} is already registered.', 'danger')
            return render_template('students/create.html', form=form)
            
        res_user = supabase.table('users').select('id').eq('username', form.username.data).execute()
        if res_user.data:
            flash(f'Username {form.username.data} is already taken.', 'danger')
            return render_template('students/create.html', form=form)
        
        # 1. Create User
        user_data = {
            'name': form.name.data,
            'email': form.email.data,
            'username': form.username.data,
            'user_type': 'student',
            'phone': form.phone.data,
            'dob': str(form.dob.data) if form.dob.data else None,
            'gender': form.gender.data,
            'address': form.address.data,
            'bg_id': form.blood_group_id.data if form.blood_group_id.data > 0 else None,
            'password': generate_password_hash(form.password.data)
        }
        
        try:
            res_u = supabase.table('users').insert(user_data).execute()
            new_user_id = res_u.data[0]['id']
            
            # 2. Create Student Record
            student_data = {
                'user_id': new_user_id,
                'my_class_id': form.my_class_id.data,
                'section_id': form.section_id.data,
                'my_parent_id': form.my_parent_id.data if form.my_parent_id.data > 0 else None,
                'adm_no': form.adm_no.data,
                'year_admitted': form.year_admitted.data,
                'session': form.session.data,
                'house': form.house.data,
                'age': form.age.data
            }
            supabase.table('student_records').insert(student_data).execute()
            
            flash(f'Student {form.name.data} created successfully!', 'success')
            return redirect(url_for('students.index'))
            
        except Exception as e:
             flash(f'Creation failed: {str(e)}', 'danger')
    
    return render_template('students/create.html', form=form)


@students_bp.route('/<int:id>')
@login_required
def show(id):
    """Show student details"""
    supabase = get_db()
    
    # Get Student Record with User and Parent
    res = supabase.table('student_records').select(
        '*, user:users(*), my_class:my_classes(*), section:sections(*)'
    ).eq('id', id).execute()
    
    if not res.data:
        abort(404)
        
    student_record = SupabaseModel(res.data[0])
    
    # Check permissions
    if not (current_user.is_admin() or current_user.is_teacher() or 
            current_user.id == student_record.user_id or 
            current_user.id == student_record.my_parent_id):
        flash('You do not have permission to view this student', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Need to fetch parent details if my_parent_id exists, 
    # but eager loading user:users(*) might have fetched the student user data, not parent.
    # Actually, FK relationship 'user' points to student's user account.
    # 'my_parent_id' is an integer ID pointing to Users table.
    
    parent = None
    if student_record.my_parent_id:
        res_p = supabase.table('users').select('*').eq('id', student_record.my_parent_id).execute()
        if res_p.data:
            parent = SupabaseModel(res_p.data[0])
            # Attach parent object to student_record for template use if needed, 
            # e.g. student_record.parent = parent (SupabaseModel allows setting attrs)
            student_record.parent = parent

    return render_template('students/show.html', student_record=student_record)


@students_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """Edit student"""
    supabase = get_db()
    
    # Fetch existing
    res = supabase.table('student_records').select('*, user:users(*)').eq('id', id).execute()
    if not res.data: abort(404)
    student_data = res.data[0]
    student_record = SupabaseModel(student_data)
    user_data = student_data['user'] # Nested dict
    user = SupabaseModel(user_data)
    
    form = StudentForm(obj=user)
    
    # Populate choices
    res_c = supabase.table('my_classes').select('id, name').execute()
    form.my_class_id.choices = [(c['id'], c['name']) for c in res_c.data]
    
    res_s = supabase.table('sections').select('id, name').eq('active', True).execute()
    form.section_id.choices = [(s['id'], s['name']) for s in res_s.data]
    
    res_p = supabase.table('users').select('id, name').eq('user_type', 'parent').execute()
    form.my_parent_id.choices = [(p['id'], p['name']) for p in res_p.data]
    form.my_parent_id.choices.insert(0, (0, 'Select Parent'))
    
    res_bg = supabase.table('blood_groups').select('id, name').execute()
    form.blood_group_id.choices = [(b['id'], b['name']) for b in res_bg.data]
    form.blood_group_id.choices.insert(0, (0, 'Select Blood Group'))
    
    # Handling SelectField population for state/lga/nationality if they exist in DB
    # Assuming tables 'states', 'lgas', 'nationalities' exist or we remove if not critical 
    # The original generic 'edit' usually expects these. I will mock empty or fetch if they exist.
    # For now, let's assume they might not be critical or we strictly need them.
    # The user provided query: State.query.all()
    try:
        res_st = supabase.table('states').select('id, name').execute()
        form.state_id.choices = [(s['id'], s['name']) for s in res_st.data]
    except: form.state_id.choices = []

    try:
        res_lg = supabase.table('lgas').select('id, name').execute()
        form.lga_id.choices = [(l['id'], l['name']) for l in res_lg.data]
    except: form.lga_id.choices = []
    
    try:
        res_n = supabase.table('nationalities').select('id, name').execute()
        form.nationality_id.choices = [(n['id'], n['name']) for n in res_n.data]
    except: form.nationality_id.choices = []

    # Pre-populate form with student_record specific fields that are not in User
    if request.method == 'GET':
        form.my_class_id.data = student_record.my_class_id
        form.section_id.data = student_record.section_id
        form.my_parent_id.data = student_record.my_parent_id or 0
        form.blood_group_id.data = user.bg_id or 0
        
    if form.validate_on_submit():
        # Update User
        user_updates = {
            'name': form.name.data,
            'email': form.email.data,
            'username': form.username.data,
            'phone': form.phone.data,
            'dob': str(form.dob.data) if form.dob.data else None,
            'gender': form.gender.data,
            'address': form.address.data,
            'bg_id': form.blood_group_id.data if form.blood_group_id.data > 0 else None
            # Do not update password here usually, or handle separately
        }
        supabase.table('users').update(user_updates).eq('id', user.id).execute()
        
        # Update Student Record
        student_updates = {
            'my_class_id': form.my_class_id.data,
            'section_id': form.section_id.data,
            'my_parent_id': form.my_parent_id.data if form.my_parent_id.data > 0 else None
        }
        supabase.table('student_records').update(student_updates).eq('id', id).execute()
        
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students.show', id=id))
    
    return render_template('students/edit.html', form=form, student_record=student_record)


@students_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Delete student"""
    supabase = get_db()
    
    # Get student record to find user_id
    res = supabase.table('student_records').select('user_id').eq('id', id).execute()
    if not res.data:
        abort(404)
        
    user_id = res.data[0]['user_id']
    
    # Delete Student Record first (if no cascade)
    supabase.table('student_records').delete().eq('id', id).execute()
    
    # Delete User
    supabase.table('users').delete().eq('id', user_id).execute()
    
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students.index'))


@students_bp.route('/graduated')
@login_required
@admin_required
def graduated():
    """List graduated students"""
    supabase = get_db()
    res = supabase.table('student_records').select('*, user:users(*)').eq('grad', True).execute()
    students = SupabaseModel.from_list(res.data)
    return render_template('students/graduated.html', students=students)


@students_bp.route('/<int:id>/not-graduated', methods=['POST'])
@login_required
@admin_required
def not_graduated(id):
    """Mark student as not graduated"""
    supabase = get_db()
    supabase.table('student_records').update({'grad': False, 'grad_date': None}).eq('id', id).execute()
    
    flash('Student marked as not graduated', 'success')
    return redirect(url_for('students.graduated'))


@students_bp.route('/reset-pass/<int:st_id>', methods=['POST'])
@login_required
@admin_required
def reset_pass(st_id):
    """Reset student password"""
    supabase = get_db()
    
    res = supabase.table('student_records').select('*, user:users(*)').eq('id', st_id).execute()
    if not res.data: abort(404)
    student_record = SupabaseModel(res.data[0])
    user = student_record.user # SupabaseModel accessible via attribute if joined correctly. 
    # But wait, SupabaseModel logic:
    # res.data[0] = {'id':..., 'user': {'id':..., 'name':...}}
    # student_record.user will be a dict unless I wrap it explicitly or SupabaseModel handles recursion (it doesn't by default).
    # SupabaseModel just does setattr(self, key, value). So student_record.user is a DICT.
    
    # Fix: Wrap it for object access if needed, or just use dict access.
    # User.set_password uses self.password_hash = ...
    # We must replicate set_password logic here: hash and update DB.
    
    new_pass = student_record.adm_no
    new_hash = generate_password_hash(new_pass)
    
    # Update User table
    # student_record.user is a dict, so student_record.user['id']
    user_id = student_record.user['id']
    supabase.table('users').update({'password': new_hash}).eq('id', user_id).execute()
    
    flash(f'Password reset for {student_record.user["name"]}. New password: {new_pass}', 'success')
    return redirect(url_for('students.show', id=st_id))


@students_bp.route('/promotion', methods=['GET', 'POST'])
@login_required
@admin_required
def promotion():
    """Promote students"""
    supabase = get_db()
    if request.method == 'POST':
        from_class = request.form.get('from_class')
        from_section = request.form.get('from_section')
        to_class = request.form.get('to_class')
        to_section = request.form.get('to_section')
        from_session = request.form.get('from_session')
        to_session = request.form.get('to_session')
        
        return redirect(url_for('students.promotion_selector',
                              fc=from_class, fs=from_section,
                              tc=to_class, ts=to_section,
                              from_session=from_session, to_session=to_session))
    
    res_c = supabase.table('my_classes').select('*').execute()
    classes = SupabaseModel.from_list(res_c.data)
    return render_template('students/promotion.html', classes=classes)


@students_bp.route('/promotion/selector')
@login_required
@admin_required
def promotion_selector():
    """Select students for promotion"""
    supabase = get_db()
    fc = request.args.get('fc', type=int)
    fs = request.args.get('fs', type=int)
    tc = request.args.get('tc', type=int)
    ts = request.args.get('ts', type=int)
    from_session = request.args.get('from_session')
    to_session = request.args.get('to_session')
    
    res_s = supabase.table('student_records').select('*, user:users(*)').eq('my_class_id', fc).eq('section_id', fs).eq('session', from_session).execute()
    students = SupabaseModel.from_list(res_s.data)
    
    res_fc = supabase.table('my_classes').select('*').eq('id', fc).execute()
    from_class = SupabaseModel(res_fc.data[0]) if res_fc.data else None
    
    res_tc = supabase.table('my_classes').select('*').eq('id', tc).execute()
    to_class = SupabaseModel(res_tc.data[0]) if res_tc.data else None
    
    return render_template('students/promotion_selector.html',
                         students=students, from_class=from_class,
                         to_class=to_class, tc=tc, ts=ts,
                         from_session=from_session, to_session=to_session)


@students_bp.route('/promotion/promote', methods=['POST'])
@login_required
@admin_required
def promote():
    """Execute student promotion"""
    supabase = get_db()
    student_ids = request.form.getlist('student_ids[]')
    to_class = request.form.get('to_class', type=int)
    to_section = request.form.get('to_section', type=int)
    to_session = request.form.get('to_session')
    
    for student_id in student_ids:
        res_sr = supabase.table('student_records').select('*').eq('id', student_id).execute()
        if res_sr.data:
            student_record = res_sr.data[0]
            # Create promotion record
            promotion = {
                'student_id': student_record['user_id'],
                'from_class': student_record['my_class_id'],
                'from_section': student_record['section_id'],
                'to_class': to_class,
                'to_section': to_section,
                'from_session': student_record['session'],
                'to_session': to_session
            }
            supabase.table('promotions').insert(promotion).execute()
            
            # Update student record
            updates = {
                'my_class_id': to_class,
                'section_id': to_section,
                'session': to_session
            }
            supabase.table('student_records').update(updates).eq('id', student_id).execute()
    
    flash(f'{len(student_ids)} students promoted successfully!', 'success')
    return redirect(url_for('students.index'))


@students_bp.route('/promotion/manage')
@login_required
@admin_required
def promotion_manage():
    """Manage promotions"""
    supabase = get_db()
    res = supabase.table('promotions').select('*, student:users(*), from_cls:my_classes!from_class(*), to_cls:my_classes!to_class(*)').order('created_at', desc=True).execute()
    promotions = SupabaseModel.from_list(res.data)
    # Note: Joins with alias 'from_cls' for 'my_classes' at foreign key 'from_class' might need explicit FK hint in Query.
    # Supabase syntax: select('*, student:users(*), from_cls:my_classes!from_class(*)')
    # Assuming FK exists. If not, simple select and manual fetch.
    return render_template('students/promotion_manage.html', promotions=promotions)


@students_bp.route('/promotion/reset/<int:pid>', methods=['POST'])
@login_required
@admin_required
def promotion_reset(pid):
    """Reset a promotion"""
    supabase = get_db()
    res_p = supabase.table('promotions').select('*').eq('id', pid).execute()
    
    if res_p.data:
        promotion = res_p.data[0]
        
        # Find student record
        res_s = supabase.table('student_records').select('id').eq('user_id', promotion['student_id']).execute()
        
        if res_s.data:
            s_id = res_s.data[0]['id']
            # Revert
            updates = {
                'my_class_id': promotion['from_class'],
                'section_id': promotion['from_section'],
                'session': promotion['from_session']
            }
            supabase.table('student_records').update(updates).eq('id', s_id).execute()
        
        # Delete promotion
        supabase.table('promotions').delete().eq('id', pid).execute()
    
    flash('Promotion reset successfully!', 'success')
    return redirect(url_for('students.promotion_manage'))
