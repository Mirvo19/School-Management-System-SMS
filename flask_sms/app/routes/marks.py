"""
Marks/Grades management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import Mark, Exam, Subject, StudentRecord, MyClass, User, db
from app.supabase_db import get_db, SupabaseModel
from app.forms.mark_forms import MarkForm
from app.utils.helpers import teacher_or_admin_required

from datetime import datetime

marks_bp = Blueprint('marks', __name__)


@marks_bp.route('/')
@login_required
@teacher_or_admin_required
def index():
    """Marks management page"""
    supabase = get_db()
    res_e = supabase.table('exams').select('*').execute()
    res_s = supabase.table('subjects').select('*').execute()
    res_c = supabase.table('my_classes').select('*').execute()
    
    exams = SupabaseModel.from_list(res_e.data)
    subjects = SupabaseModel.from_list(res_s.data)
    classes = SupabaseModel.from_list(res_c.data)
    
    return render_template('marks/index.html', exams=exams, subjects=subjects, classes=classes)


@marks_bp.route('/manage/<int:exam_id>/<int:subject_id>/<int:class_id>')
@login_required
@teacher_or_admin_required
def manage(exam_id, subject_id, class_id):
    """Manage marks for exam, subject, and class"""
    supabase = get_db()
    
    # Fetch Exam, Subject
    res_ex = supabase.table('exams').select('*').eq('id', exam_id).execute()
    res_sub = supabase.table('subjects').select('*').eq('id', subject_id).execute()
    
    if not res_ex.data or not res_sub.data:
        abort(404)
        
    exam = SupabaseModel(res_ex.data[0])
    subject = SupabaseModel(res_sub.data[0])
    
    # Fetch Students in Class
    # Need user name, so join user
    res_stu = supabase.table('student_records').select('*, user:users(*)').eq('my_class_id', class_id).execute()
    students = SupabaseModel.from_list(res_stu.data)
    
    # Fetch existing Marks for this batch
    # Filter by exam, subject, and class_id (optional to filter by class in marks table if populated, else by student_ids)
    # Marks table has my_class_id, so we use it.
    res_marks = supabase.table('marks').select('*').eq('exam_id', exam_id).eq('subject_id', subject_id).eq('my_class_id', class_id).execute()
    
    marks_lookup = { m['student_id']: SupabaseModel(m) for m in res_marks.data }
    
    # Map marks to students dict for template: marks[student.id] = mark_obj
    marks = {}
    for student in students:
        # student.user_id is the user id, student.id is record id. 
        # Marks usually link to User ID (student_id col in Marks table usually refers to user table id based on foreign key)
        # Checking original models.py: Mark.student_id FK users.id.
        marks[student.id] = marks_lookup.get(student.user_id)
    
    return render_template('marks/manage.html',
                         exam=exam, subject=subject,
                         students=students, marks=marks)


@marks_bp.route('/save', methods=['POST'])
@login_required
@teacher_or_admin_required
def save():
    """Save marks"""
    # This function iterates through students and updates marks.
    # In Supabase/SQL, bulk upsert is better, but iterating is safer for logic if we need to calc totals individually.
    
    exam_id = request.form.get('exam_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    class_id = request.form.get('class_id', type=int)
    
    supabase = get_db()
    
    # Get all students for class to iterate form data
    res_stu = supabase.table('student_records').select('*').eq('my_class_id', class_id).execute()
    students = SupabaseModel.from_list(res_stu.data)
    
    # Get exam info for 'year'
    res_ex = supabase.table('exams').select('year').eq('id', exam_id).execute()
    exam_year = res_ex.data[0]['year'] if res_ex.data else None
    
    upsert_data = []
    
    for student in students:
        t1 = request.form.get(f't1_{student.id}', type=int)
        exams = request.form.get(f'exams_{student.id}', type=int)
        
        # Original logic calculates total. 
        # Note: If input is empty string, type=int returns None.
        
        val_t1 = t1 or 0
        val_exams = exams or 0
        total = val_t1 + val_exams
        
        # Prepare record
        # filtering using match columns for upsert usually requires a unique constraint 
        # on (exam_id, subject_id, student_id).
        # Assuming Supabase/Postgres has this constraint (or ID based update).
        # Since we don't have the mark ID easily here without querying, 
        # we might need to check if exists or use upsert if schema supports it.
        # Fallback: Select existing mark ID to update, else insert.
        
        # Optimize: We did fetch marks in manage(), but here we are in a disconnected POST.
        # Queries inside loop are bad. But safer for now during migration.
        
        existing = supabase.table('marks').select('id').eq('exam_id', exam_id).eq('subject_id', subject_id).eq('student_id', student.user_id).execute()
        
        row = {
            'exam_id': exam_id,
            'subject_id': subject_id,
            'student_id': student.user_id,
            'my_class_id': class_id,
            'section_id': student.section_id,
            'year': exam_year,
            't1': val_t1,
            'exams': val_exams,
            'total': total
        }
        
        if existing.data:
            # Update
            supabase.table('marks').update(row).eq('id', existing.data[0]['id']).execute()
        else:
            # Insert
            supabase.table('marks').insert(row).execute()

    flash('Marks saved successfully!', 'success')
    return redirect(url_for('marks.manage',
                          exam_id=exam_id,
                          subject_id=subject_id,
                          class_id=class_id))


def calculate_grade(percentage):
    if percentage >= 90: return 'A'
    elif percentage >= 80: return 'B'
    elif percentage >= 70: return 'C'
    elif percentage >= 60: return 'D'
    elif percentage >= 50: return 'E'
    else: return 'F'

def calculate_gpa(percentage):
    if percentage >= 90: return 4.0
    elif percentage >= 80: return 3.6
    elif percentage >= 70: return 3.2
    elif percentage >= 60: return 2.8
    elif percentage >= 50: return 2.4
    else: return 0.0

@marks_bp.route('/results/<int:exam_id>/<int:class_id>')
@login_required
@teacher_or_admin_required
def class_results(exam_id, class_id):
    """Generate class results report"""
    supabase = get_db()
    
    res_ex = supabase.table('exams').select('*').eq('id', exam_id).execute()
    res_cl = supabase.table('my_classes').select('*').eq('id', class_id).execute()
    
    if not res_ex.data or not res_cl.data:
        abort(404)
        
    exam = SupabaseModel(res_ex.data[0])
    my_class = SupabaseModel(res_cl.data[0])
    
    # Students
    res_st = supabase.table('student_records').select('*, user:users(*)').eq('my_class_id', class_id).execute()
    students = SupabaseModel.from_list(res_st.data)
    
    # Subjects
    # Subjects might be associated to class, or all subjects
    res_sub = supabase.table('subjects').select('*').eq('my_class_id', class_id).execute()
    subjects = SupabaseModel.from_list(res_sub.data)
    
    if not subjects:
        res_sub_all = supabase.table('subjects').select('*').execute()
        subjects = SupabaseModel.from_list(res_sub_all.data)

    # Bulk fetch marks for this exam and class to avoid N+1 inside loop
    res_marks = supabase.table('marks').select('*').eq('exam_id', exam_id).eq('my_class_id', class_id).execute()
    # Index by (student_id, subject_id) -> record
    marks_map = { (m['student_id'], m['subject_id']): m for m in res_marks.data }

    results = []
    
    for student in students:
        student_data = {
            'student': student,
            'marks': {},
            'total_score': 0,
            'subject_count': 0
        }
        
        for subject in subjects:
            # mark_data = marks_map.get( (student.user_id, subject.id) )
            # student.user_id is int or str depending on DB. Supabase returns ints as ints usually.
            mark_data = marks_map.get( (student.user_id, subject.id) )
            
            score = mark_data['total'] if mark_data else 0
            student_data['marks'][subject.id] = score
            student_data['total_score'] += score
            student_data['subject_count'] += 1
            
        # Avoid division by zero
        count = student_data['subject_count'] if student_data['subject_count'] > 0 else 1
        percentage = student_data['total_score'] / count
        
        student_data['percentage'] = percentage
        student_data['grade'] = calculate_grade(percentage)
        student_data['gpa'] = calculate_gpa(percentage)
        
        results.append(student_data)
        
    # Class Statistics
    if not results:
        flash('No data found for this class.', 'warning')
        return redirect(url_for('marks.index'))

    # Topper
    topper = max(results, key=lambda x: x['total_score'])
    
    # Subject Highs
    subject_highs = {}
    for subject in subjects:
        high_score = 0
        scorer = None
        for r in results:
            s = r['marks'].get(subject.id, 0)
            if s > high_score:
                high_score = s
                scorer = r['student'].user['name'] if isinstance(r['student'].user, dict) else r['student'].user.name
        subject_highs[subject.id] = {'score': high_score, 'scorer': scorer}
        
    # Class Average
    class_avg = sum(r['percentage'] for r in results) / len(results)
    
    return render_template('marks/class_results.html',
                         exam=exam,
                         my_class=my_class,
                         subjects=subjects,
                         results=results,
                         topper=topper,
                         subject_highs=subject_highs,
                         class_avg=class_avg)


@marks_bp.route('/result/<int:exam_id>/<int:student_id>')
@login_required
@teacher_or_admin_required
def student_result(exam_id, student_id):
    """Generate individual student result report"""
    supabase = get_db()
    
    res_ex = supabase.table('exams').select('*').eq('id', exam_id).execute()
    if not res_ex.data: abort(404)
    exam = SupabaseModel(res_ex.data[0])
    
    res_u = supabase.table('users').select('*').eq('id', student_id).execute()
    if not res_u.data: abort(404)
    student = SupabaseModel(res_u.data[0])
    
    res_st = supabase.table('student_records').select('*, my_class:my_classes(*)').eq('user_id', student_id).execute()
    if not res_st.data:
        flash('Student record not found.', 'danger')
        return redirect(url_for('marks.index'))
    student_record = SupabaseModel(res_st.data[0])


    my_class = student_record.my_class
    # my_class might be dict or SupabaseModel depending on nesting. 
    # SupabaseModel wrapper usually recursively wraps if we enforced it, 
    # but currently it just sets attributes.
    # If student_record.my_class is a dict, we can wrap it or use it as is if template allows dict access 
    # (Jinja2 allows dot access on dicts too? No, it prefers dot for objects. 
    # Actually Jinja2 dot works for dict keys too! But let's be safe).
    # Since SupabaseModel __init__ sets attr, if value is dict, it sets self.my_class = dict.
    # Jinja2: {{ record.my_class.name }} works on dict.
    
    # Get Subjects
    class_id = my_class['id'] if isinstance(my_class, dict) else my_class.id
    
    res_sub = supabase.table('subjects').select('*').eq('my_class_id', class_id).execute()
    subjects = SupabaseModel.from_list(res_sub.data)
    if not subjects:
        res_all = supabase.table('subjects').select('*').execute()
        subjects = SupabaseModel.from_list(res_all.data)

    marks_data = []
    total_score = 0
    subject_count = 0
    
    # Bulk Fetch Marks
    res_marks = supabase.table('marks').select('*').eq('exam_id', exam_id).eq('student_id', student_id).execute()
    marks_map = { m['subject_id']: m for m in res_marks.data }
    
    for subject in subjects:
        mark = marks_map.get(subject.id)
        
        t1 = mark['t1'] if mark else 0
        exams = mark['exams'] if mark else 0
        total = mark['total'] if mark else 0
        
        grade = calculate_grade(total) 
        sub_remark = mark['teacher_remark'] if mark and 'teacher_remark' in mark else ""
        
        marks_data.append({
            'subject': subject,
            't1': t1,
            'exams': exams,
            'total': total,
            'grade': grade,
            'remark': sub_remark
        })
        
        total_score += total
        subject_count += 1
        
    count = subject_count if subject_count > 0 else 1
    percentage = total_score / count
    overall_grade = calculate_grade(percentage)
    gpa = calculate_gpa(percentage)
    
    return render_template('marks/student_result.html',
                         exam=exam,
                         student=student,
                         student_record=student_record,
                         my_class=my_class,
                         marks_data=marks_data,
                         total_score=total_score,
                         percentage=percentage,
                         overall_grade=overall_grade,
                         gpa=gpa,
                         now=datetime.now)
