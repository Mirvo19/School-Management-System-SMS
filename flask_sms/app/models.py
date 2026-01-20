"""
Database models for Flask SMS application
This module contains all SQLAlchemy models converted from Laravel Eloquent models
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model - teachers, students, parents, admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(191), nullable=False)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(100))
    phone2 = db.Column(db.String(100))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    photo = db.Column(db.String(255))
    address = db.Column(db.Text)
    bg_id = db.Column(db.Integer, db.ForeignKey('blood_groups.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'))
    lga_id = db.Column(db.Integer, db.ForeignKey('lgas.id'))
    nal_id = db.Column(db.Integer, db.ForeignKey('nationalities.id'))
    email_verified_at = db.Column(db.DateTime)
    remember_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    blood_group = db.relationship('BloodGroup', backref='users')
    state = db.relationship('State', backref='users')
    lga = db.relationship('Lga', backref='users')
    nationality = db.relationship('Nationality', backref='users')
    student_record = db.relationship('StudentRecord', backref='user', uselist=False, foreign_keys='StudentRecord.user_id')
    staff_record = db.relationship('StaffRecord', backref='user', uselist=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.user_type == 'super_admin'
    
    def is_teacher(self):
        """Check if user is teacher"""
        return self.user_type == 'teacher'
    
    def is_student(self):
        """Check if user is student"""
        return self.user_type == 'student'
    
    def is_parent(self):
        """Check if user is parent"""
        return self.user_type == 'parent'

    def is_accountant(self):
        """Check if user is accountant"""
        return self.user_type == 'accountant'


class UserType(db.Model):
    """User types/roles"""
    __tablename__ = 'user_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BloodGroup(db.Model):
    """Blood group model"""
    __tablename__ = 'blood_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class State(db.Model):
    """States model"""
    __tablename__ = 'states'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lgas = db.relationship('Lga', backref='state', lazy='dynamic')


class Lga(db.Model):
    """Local Government Areas"""
    __tablename__ = 'lgas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Nationality(db.Model):
    """Nationalities model"""
    __tablename__ = 'nationalities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MyClass(db.Model):
    """Classes/Grades model"""
    __tablename__ = 'my_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    class_type_id = db.Column(db.Integer, db.ForeignKey('class_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class_type = db.relationship('ClassType', backref='classes')
    sections = db.relationship('Section', backref='my_class', lazy='dynamic')
    students = db.relationship('StudentRecord', backref='my_class', lazy='dynamic')


class ClassType(db.Model):
    """Class types (Primary, Secondary, etc.)"""
    __tablename__ = 'class_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Section(db.Model):
    """Class sections (A, B, C, etc.)"""
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    teacher = db.relationship('User', foreign_keys=[teacher_id])


class StudentRecord(db.Model):
    """Student records and enrollment"""
    __tablename__ = 'student_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    my_parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    dorm_id = db.Column(db.Integer, db.ForeignKey('dorms.id'))
    dorm_room_no = db.Column(db.String(50))
    adm_no = db.Column(db.String(100), unique=True, nullable=False)
    year_admitted = db.Column(db.Integer, nullable=False)
    house = db.Column(db.String(100))
    age = db.Column(db.Integer)
    wd = db.Column(db.Boolean, default=False)  # Withdrawn
    wd_date = db.Column(db.Date)
    grad = db.Column(db.Boolean, default=False)  # Graduated
    grad_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    section = db.relationship('Section', backref='students')
    my_parent = db.relationship('User', foreign_keys=[my_parent_id])
    dorm = db.relationship('Dorm', backref='students')


class StaffRecord(db.Model):
    """Staff/Teacher records"""
    __tablename__ = 'staff_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    code = db.Column(db.String(100), unique=True)
    emp_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subject(db.Model):
    """Subjects model"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    my_class = db.relationship('MyClass', backref='subjects')
    teacher = db.relationship('User', backref='subjects_taught')


class Exam(db.Model):
    """Exams model"""
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer)
    year = db.Column(db.Integer, nullable=False)
    term = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ExamRecord(db.Model):
    """Exam records for students"""
    __tablename__ = 'exam_records'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer)
    ave = db.Column(db.Float)
    pos = db.Column(db.Integer)
    af = db.Column(db.Integer)
    ps = db.Column(db.Integer)
    p_comment = db.Column(db.Text)
    t_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    exam = db.relationship('Exam', backref='records')
    student = db.relationship('User', backref='exam_records')


class Mark(db.Model):
    """Marks/Grades for exams"""
    __tablename__ = 'marks'
    
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    tex1 = db.Column(db.Integer)
    tex2 = db.Column(db.Integer)
    tex3 = db.Column(db.Integer)
    exm = db.Column(db.Integer)
    t1 = db.Column(db.Integer)
    t2 = db.Column(db.Integer)
    t3 = db.Column(db.Integer)
    t4 = db.Column(db.Integer)
    tca = db.Column(db.Integer)
    exams = db.Column(db.Integer)
    total = db.Column(db.Integer)
    grade_id = db.Column(db.Integer, db.ForeignKey('grades.id'))
    teacher_remark = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    exam = db.relationship('Exam')
    student = db.relationship('User')
    subject = db.relationship('Subject')
    grade = db.relationship('Grade')


class Grade(db.Model):
    """Grading system"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    class_type_id = db.Column(db.Integer, db.ForeignKey('class_types.id'))
    mark_from = db.Column(db.Integer, nullable=False)
    mark_to = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class_type = db.relationship('ClassType')


class Dorm(db.Model):
    """Dormitories model"""
    __tablename__ = 'dorms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment(db.Model):
    """Payment types"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'))
    description = db.Column(db.Text)
    year = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    my_class = db.relationship('MyClass')


class PaymentRecord(db.Model):
    """Payment records for students"""
    __tablename__ = 'payment_records'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    amount_paid = db.Column(db.Float, default=0)
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    payment = db.relationship('Payment')
    student = db.relationship('User')


class Receipt(db.Model):
    """Payment receipts"""
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    pr_id = db.Column(db.Integer, db.ForeignKey('payment_records.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    year = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    payment_record = db.relationship('PaymentRecord', backref='receipts')


class Pin(db.Model):
    """Exam/Result PINs"""
    __tablename__ = 'pins'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    used = db.Column(db.Boolean, default=False)
    times_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
    student = db.relationship('User', foreign_keys=[student_id])


class TimeTable(db.Model):
    """Timetable model"""
    __tablename__ = 'time_tables'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    my_class_id = db.Column(db.Integer, db.ForeignKey('my_classes.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    year = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    my_class = db.relationship('MyClass')
    exam = db.relationship('Exam')


class TimeTableRecord(db.Model):
    """Timetable records"""
    __tablename__ = 'time_table_records'
    
    id = db.Column(db.Integer, primary_key=True)
    tt_id = db.Column(db.Integer, db.ForeignKey('time_tables.id'), nullable=False)
    ts_id = db.Column(db.Integer, db.ForeignKey('time_slots.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    timestamp_from = db.Column(db.Time)
    timestamp_to = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    time_table = db.relationship('TimeTable', backref='records')
    time_slot = db.relationship('TimeSlot', foreign_keys=[ts_id])
    subject = db.relationship('Subject')


class TimeSlot(db.Model):
    """Time slots for timetable"""
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    ttr_id = db.Column(db.Integer, db.ForeignKey('time_table_records.id'))
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    full = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Promotion(db.Model):
    """Student promotions"""
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_class = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    from_section = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    to_class = db.Column(db.Integer, db.ForeignKey('my_classes.id'), nullable=False)
    to_section = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    from_session = db.Column(db.String(50), nullable=False)
    to_session = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='promoted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('User')


class Setting(db.Model):
    """System settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Skill(db.Model):
    """Skills for assessments"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill_type = db.Column(db.String(100))
    class_type_id = db.Column(db.Integer, db.ForeignKey('class_types.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class_type = db.relationship('ClassType')


class Book(db.Model):
    """Library books"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    isbn = db.Column(db.String(50), unique=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subject = db.relationship('Subject')


class BookRequest(db.Model):
    """Book borrowing requests"""
    __tablename__ = 'book_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    issued_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    returned_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    book = db.relationship('Book')
    user = db.relationship('User')
