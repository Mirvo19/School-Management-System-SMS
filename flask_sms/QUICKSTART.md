# Quick Start Guide - Flask SMS

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
cd flask_sms
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the example:
```bash
copy .env.example .env
```

Edit `.env` and update:
- `SECRET_KEY` - Generate using: `python -c "import secrets; print(secrets.token_hex(32))"`
- `SCHOOL_NAME` - Your school's name
- Database and mail settings as needed

### 3. Initialize Database

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

**OR** use the simplified run script that auto-creates tables:
```bash
python run.py
```

### 4. Seed Database with Initial Data

```bash
python seed.py
```

This creates:
- Admin user (username: `admin`, password: `admin123`)
- Blood groups
- User types
- Class types and sample classes
- Grading system
- Sample states and nationalities

### 5. Run the Application

```bash
# Development mode
python app.py

# Or using run.py
python run.py

# Or using Flask CLI
flask run
```

### 6. Access the Application

Open browser: `http://localhost:5000`

Login with:
- **Username**: admin
- **Password**: admin123

⚠️ **Change the default password immediately!**

## Common Tasks

### Create a New Admin User (Python Shell)

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(
        name='John Doe',
        email='john@school.com',
        username='johndoe',
        user_type='super_admin'
    )
    admin.set_password('secure_password')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### Reset Database

```bash
# Delete database file
del sms_dev.db  # Windows
rm sms_dev.db   # Linux/Mac

# Recreate
python run.py
python seed.py
```

### Production Deployment

1. Set environment to production:
   ```
   FLASK_ENV=production
   ```

2. Use a production database (PostgreSQL/MySQL):
   ```
   DATABASE_URL=postgresql://user:password@localhost/sms_db
   ```

3. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. Set up Nginx as reverse proxy (recommended)

## Troubleshooting

### Import Errors

If you get import errors, ensure you're in the correct directory:
```bash
cd flask_sms
python app.py
```

### Database Errors

Delete the database and migrations folder, then restart:
```bash
rmdir /s migrations  # Windows
rm -rf migrations    # Linux/Mac
del sms_dev.db
flask db init
flask db migrate -m "Initial"
flask db upgrade
python seed.py
```

### Port Already in Use

Change the port in `app.py` or `run.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

## Features Overview

- ✅ User authentication and authorization
- ✅ Student management (CRUD)
- ✅ Class and section management
- ✅ Subject allocation
- ✅ Exam and marks management
- ✅ Timetable creation
- ✅ Payment tracking
- ✅ Dormitory management
- ✅ PIN system for results
- ✅ Role-based access control
- ✅ Responsive Bootstrap UI

## Next Steps

1. Customize school settings
2. Add classes and sections
3. Create teacher accounts
4. Enroll students
5. Set up subjects
6. Create academic calendar

## Need Help?

- Check README.md for detailed documentation
- Review code comments in models.py and routes
- Examine existing templates for UI patterns
