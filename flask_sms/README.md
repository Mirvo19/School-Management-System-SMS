# Flask School Management System (SMS)

A comprehensive web-based School Management System built with Python Flask, converted from the original Laravel application.

## Features

- **User Management**: Admin, Teachers, Students, and Parents with role-based access control
- **Student Management**: Admission, enrollment, promotion, and graduation tracking
- **Academic Management**:
  - Class and section management
  - Subject allocation
  - Teacher assignments
- **Examination System**:
  - Exam creation and management
  - Mark/grade entry and calculation
  - Result generation
- **Timetable Management**: Create and manage class timetables
- **Payment System**: Fee management and payment tracking
- **Dormitory Management**: Hostel allocation and management
- **PIN System**: Secure result checking with PINs
- **Reports**: Generate various academic and administrative reports

## Technology Stack

- **Framework**: Flask 3.0
- **Database ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms
- **Database Migrations**: Flask-Migrate (Alembic)
- **Frontend**: Bootstrap 5, Font Awesome
- **Template Engine**: Jinja2

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   cd flask_sms
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file and set your configurations:
   - `SECRET_KEY`: Generate a secure secret key
   - `DATABASE_URL`: Your database connection string
   - `SCHOOL_NAME`: Your school name
   - Mail settings for email notifications

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create initial admin user** (optional):
   ```python
   python
   >>> from app import create_app, db
   >>> from app.models import User
   >>> app = create_app()
   >>> with app.app_context():
   ...     admin = User(name='Admin', email='admin@school.com', username='admin', user_type='super_admin')
   ...     admin.set_password('admin123')
   ...     db.session.add(admin)
   ...     db.session.commit()
   >>> exit()
   ```

7. **Run the application**:
   ```bash
   # Development mode
   python app.py

   # Or using Flask CLI
   flask run
   ```

8. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
flask_sms/
│
├── app/
│   ├── forms/              # WTForms form definitions
│   │   ├── auth_forms.py
│   │   ├── student_forms.py
│   │   └── ...
│   │
│   ├── routes/             # Blueprint routes
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── students.py
│   │   └── ...
│   │
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── ...
│   │
│   ├── utils/              # Helper utilities
│   │   ├── helpers.py
│   │   ├── error_handlers.py
│   │   └── template_helpers.py
│   │
│   └── models.py           # SQLAlchemy models
│
├── migrations/             # Database migrations
├── uploads/               # File uploads directory
├── app.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

## Usage

### Default Login Credentials

After setting up the admin user:
- **Username**: admin
- **Password**: admin123

**Important**: Change the default password immediately after first login.

### User Roles

1. **Super Admin**: Full system access
2. **Admin**: Administrative access
3. **Teacher**: Access to teaching-related features
4. **Student**: Access to student portal
5. **Parent**: Access to children's information
6. **Accountant**: Financial management
7. **Librarian**: Library management

## Key Features Guide

### Student Management
- Add, edit, and delete students
- Assign to classes and sections
- Track admission and graduation
- Manage student promotions

### Examination System
- Create exams for different terms
- Enter marks for subjects
- Calculate grades automatically
- Generate result cards

### Timetable Management
- Create timetables for classes
- Assign subjects to time slots
- Manage teacher schedules

### Payment System
- Define payment types and amounts
- Track student payments
- Generate invoices and receipts

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables for Production
- Set `FLASK_ENV=production`
- Use a strong `SECRET_KEY`
- Configure proper database (PostgreSQL recommended)
- Set up proper mail server
- Enable HTTPS/SSL

## Contributing

This is a conversion from Laravel to Flask. Contributions to improve functionality, add features, or fix bugs are welcome.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue in the repository.

## Acknowledgments

- Original Laravel application: lav_sms
- Flask framework and extensions
- Bootstrap for UI components
