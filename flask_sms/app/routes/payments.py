"""
Payments management routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Payment, PaymentRecord, Receipt, StudentRecord, MyClass, db
from app.utils.helpers import admin_required, accountant_required

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/')
@login_required
def index():
    """List all payments"""
    payments = Payment.query.all()
    return render_template('payments/index.html', payments=payments)


@payments_bp.route('/create', methods=['GET', 'POST'])
@login_required
@accountant_required
def create():
    """Create new payment definition"""
    if request.method == 'POST':
        payment = Payment(
            title=request.form.get('title'),
            amount=request.form.get('amount'),
            description=request.form.get('description'),
            my_class_id=request.form.get('my_class_id'),
            year=request.form.get('year')
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('Payment created successfully!', 'success')
        return redirect(url_for('payments.index'))
    
    classes = MyClass.query.all()
    return render_template('payments/create.html', classes=classes)


@payments_bp.route('/manage/<int:class_id>')
@login_required
@accountant_required
def manage(class_id):
    """Manage payments for a class"""
    students = StudentRecord.query.filter_by(my_class_id=class_id).all()
    payments = Payment.query.filter_by(my_class_id=class_id).all()
    
    return render_template('payments/manage.html',
                         students=students,
                         payments=payments)


@payments_bp.route('/invoice/<int:student_id>')
@login_required
def invoice(student_id):
    """Student payment invoice"""
    student_record = StudentRecord.query.get_or_404(student_id)
    
    # Get all payments for student's class
    class_payments = Payment.query.filter_by(my_class_id=student_record.my_class_id).all()
    
    # Get existing records
    paid_records = {pr.payment_id: pr for pr in PaymentRecord.query.filter_by(student_id=student_record.user_id).all()}
    
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
            item['paid'] = paid_records[payment.id].paid
            item['payment_record_id'] = paid_records[payment.id].id
            item['amount_paid'] = paid_records[payment.id].amount_paid
        invoice_items.append(item)
    
    return render_template('payments/invoice.html',
                         student_record=student_record,
                         invoice_items=invoice_items)


@payments_bp.route('/pay/<int:student_id>/<int:payment_id>', methods=['POST'])
@login_required
@accountant_required
def pay(student_id, payment_id):
    """Process payment"""
    student_record = StudentRecord.query.get_or_404(student_id)
    payment = Payment.query.get_or_404(payment_id)
    
    record = PaymentRecord.query.filter_by(
        student_id=student_record.user_id,
        payment_id=payment.id
    ).first()
    
    if not record:
        record = PaymentRecord(
            payment_id=payment.id,
            student_id=student_record.user_id,
            year=payment.year,
            amount_paid=payment.amount,
            paid=True
        )
        db.session.add(record)
    else:
        record.paid = True
        record.amount_paid = payment.amount
    
    db.session.flush() # Ensure ID is generated
    
    # Create receipt
    receipt = Receipt(
        pr_id=record.id,
        amount_paid=payment.amount,
        year=payment.year
    )
    db.session.add(receipt)
    db.session.commit()
    
    flash(f'Payment for {payment.title} recorded successfully', 'success')
    return redirect(url_for('payments.invoice', student_id=student_id))

