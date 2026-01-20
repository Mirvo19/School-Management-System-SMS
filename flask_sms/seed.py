"""
Database seeder script
Run this to populate the database with initial data
"""
from app import create_app, db
from app.models import (
    User, BloodGroup, State, Lga, Nationality, ClassType, 
    MyClass, Section, Grade, UserType, Setting
)
from datetime import datetime


def seed_database():
    """Seed the database with initial data"""
    config_name = 'production'  # Use production config on Render
    app = create_app(config_name)
    with app.app_context():
        print("Starting database seeding...")
        
        # Create blood groups
        blood_groups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        for bg_name in blood_groups:
            if not BloodGroup.query.filter_by(name=bg_name).first():
                bg = BloodGroup(name=bg_name)
                db.session.add(bg)
        print("✓ Blood groups created")
        
        # Create user types
        user_types = [
            ('super_admin', 10),
            ('admin', 9),
            ('teacher', 5),
            ('accountant', 4),
            ('librarian', 3),
            ('parent', 2),
            ('student', 1)
        ]
        for ut_name, level in user_types:
            if not UserType.query.filter_by(name=ut_name).first():
                ut = UserType(name=ut_name, level=level)
                db.session.add(ut)
        print("✓ User types created")
        
        # Create class types
        class_types = [
            ('Nursery', 'NUR'),
            ('Primary', 'PRI'),
            ('Junior Secondary', 'JSS'),
            ('Senior Secondary', 'SSS')
        ]
        for ct_name, ct_code in class_types:
            if not ClassType.query.filter_by(code=ct_code).first():
                ct = ClassType(name=ct_name, code=ct_code)
                db.session.add(ct)
        print("✓ Class types created")
        
        db.session.commit()
        
        # Create sample classes
        primary_type = ClassType.query.filter_by(code='PRI').first()
        if primary_type:
            classes = ['Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6']
            for class_name in classes:
                if not MyClass.query.filter_by(name=class_name).first():
                    mc = MyClass(name=class_name, class_type_id=primary_type.id)
                    db.session.add(mc)
        print("✓ Sample classes created")
        
        db.session.commit()
        
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                name='System Administrator',
                email='admin@school.com',
                username='admin',
                user_type='super_admin',
                gender='male',
                code='ADMIN001'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Admin user created (username: admin, password: admin123)")
        
        db.session.commit()
        
        # Create sample nationality
        if not Nationality.query.filter_by(name='Nigerian').first():
            nationality = Nationality(name='Nigerian')
            db.session.add(nationality)
        print("✓ Sample nationality created")
        
        # Create sample states
        sample_states = ['Lagos', 'Abuja', 'Kano', 'Rivers']
        for state_name in sample_states:
            if not State.query.filter_by(name=state_name).first():
                state = State(name=state_name)
                db.session.add(state)
        print("✓ Sample states created")
        
        db.session.commit()
        
        # Create grading system
        primary_ct = ClassType.query.filter_by(code='PRI').first()
        if primary_ct:
            grades = [
                ('A+', 90, 100, 'Excellent'),
                ('A', 80, 89, 'Very Good'),
                ('B', 70, 79, 'Good'),
                ('C', 60, 69, 'Credit'),
                ('D', 50, 59, 'Pass'),
                ('E', 40, 49, 'Weak Pass'),
                ('F', 0, 39, 'Fail')
            ]
            for name, mark_from, mark_to, remark in grades:
                if not Grade.query.filter_by(name=name, class_type_id=primary_ct.id).first():
                    grade = Grade(
                        name=name,
                        class_type_id=primary_ct.id,
                        mark_from=mark_from,
                        mark_to=mark_to,
                        remark=remark
                    )
                    db.session.add(grade)
        print("✓ Grading system created")
        
        db.session.commit()
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Please change the default password after first login!")


if __name__ == '__main__':
    seed_database()
