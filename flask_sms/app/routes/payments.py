"""
Payments management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
# from app.models import Payment, PaymentRecord, Receipt, StudentRecord, MyClass, db
from app.supabase_db import get_db, SupabaseModel
from app.utils.helpers import admin_required, accountant_required

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/')
@login_required
def index():
    """List all payments"""
    supabase = get_db()
    res = supabase.table('payments').select('*, my_class:my_classes(*)').execute()
    payments = SupabaseModel.from_list(res.data)
    return render_template('payments/index.html', payments=payments)


@payments_bp.route('/create', methods=['GET', 'POST'])
@login_required
@accountant_required
def create():
    """Create new payment definition"""
    supabase = get_db()
    
    if request.method == 'POST':
        new_payment = {
            'title': request.form.get('title'),
            'amount': request.form.get('amount'),
            'description': request.form.get('description'),
            'my_class_id': request.form.get('my_class_id'),
            'year': request.form.get('year')
        }
        try:
            supabase.table('payments').insert(new_payment).execute()
            flash('Payment created successfully!', 'success')
            return redirect(url_for('payments.index'))
        except Exception as e:
            flash(f'Creation failed: {str(e)}', 'danger')
    
    res_c = supabase.table('my_classes').select('*').execute()
    classes = SupabaseModel.from_list(res_c.data)
    return render_template('payments/create.html', classes=classes)


@payments_bp.route('/manage/<int:class_id>')
@login_required
@accountant_required
def manage(class_id):
    """Manage payments for a class"""
    supabase = get_db()
    
    res_stu = supabase.table('student_records').select('*, user:users(*)').eq('my_class_id', class_id).execute()
    students = SupabaseModel.from_list(res_stu.data)
    
    res_pay = supabase.table('payments').select('*').eq('my_class_id', class_id).execute()
    payments = SupabaseModel.from_list(res_pay.data)
    
    return render_template('payments/manage.html',
                         students=students,
                         payments=payments)


@payments_bp.route('/invoice/<int:student_id>')
@login_required
def invoice(student_id):
    """Student payment invoice"""
    supabase = get_db()
    
    # Check current user permission (Student can view own, Parent view child, Admin/Accountant view all)
    # Assuming helpers logic or template handles strict permission or it's open for user if ID matches.
    
    # using student_record id (which is the param 'student_id' in URL? original code says get_or_404(student_id) on StudentRecord)
    # Wait, URL usually passes primary key. If student_id is user_id, it is different.
    # Original: StudentRecord.query.get_or_404(student_id) implies the param is the PK of StudentRecord table.
    
    res_st = supabase.table('student_records').select('*, user:users(*)').eq('id', student_id).execute()
    if not res_st.data:
        abort(404)
        
    student_record = SupabaseModel(res_st.data[0])
    
    # Get all payments for student's class
    res_pay = supabase.table('payments').select('*').eq('my_class_id', student_record.my_class_id).execute()
    class_payments = SupabaseModel.from_list(res_pay.data)
    
    # Get existing records
    # filter by student_id which is user_id in payment_records table usually
    res_pr = supabase.table('payment_records').select('*').eq('student_id', student_record.user_id).execute()
    paid_records = { pr['payment_id']: SupabaseModel(pr) for pr in res_pr.data }
    
    # Combine
    invoice_items = []
    for payment in class_payments:
        item = {
            'id': payment.id,
            'title': payment.title,
            'amount': payment.amount,
            'paid': False,
            'payment_record_id': None
        }
        if payment.id in paid_records:
            pr = paid_records[payment.id]
            item['paid'] = pr.paid
            item['payment_record_id'] = pr.id
            item['amount_paid'] = pr.amount_paid
        invoice_items.append(item)
    
    return render_template('payments/invoice.html',
                         student_record=student_record,
                         invoice_items=invoice_items)


@payments_bp.route('/pay/<int:student_id>/<int:payment_id>', methods=['POST'])
@login_required
@accountant_required
def pay(student_id, payment_id):
    """Process payment"""
    # student_id here is StudentRecord ID based on invoice route logic
    supabase = get_db()
    
    res_st = supabase.table('student_records').select('*').eq('id', student_id).execute()
    if not res_st.data: abort(404)
    student_record = SupabaseModel(res_st.data[0])
    
    res_pay = supabase.table('payments').select('*').eq('id', payment_id).execute()
    if not res_pay.data: abort(404)
    payment = SupabaseModel(res_pay.data[0])
    
    # Check if record exists
    res_pr = supabase.table('payment_records').select('*').eq('student_id', student_record.user_id).eq('payment_id', payment.id).execute()
    
    try:
        pr_id = None
        if not res_pr.data:
            # Insert
            new_pr = {
                'payment_id': payment.id,
                'student_id': student_record.user_id,
                'year': payment.year,
                'amount_paid': payment.amount,
                'paid': True
            }
            res_ins = supabase.table('payment_records').insert(new_pr).execute()
            pr_id = res_ins.data[0]['id']
        else:
            # Update
            pr_id = res_pr.data[0]['id']
            upd_pr = {
                'paid': True,
                'amount_paid': payment.amount
            }
            supabase.table('payment_records').update(upd_pr).eq('id', pr_id).execute()
        
        # Create receipt
        new_receipt = {
            'pr_id': pr_id,
            'amount_paid': payment.amount,
            'year': payment.year
        }
        supabase.table('receipts').insert(new_receipt).execute()
        
        flash(f'Payment for {payment.title} recorded successfully', 'success')
        
    except Exception as e:
        flash(f'Payment failed: {str(e)}', 'danger')

    return redirect(url_for('payments.invoice', student_id=student_id))

