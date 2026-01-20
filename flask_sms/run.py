"""
Run script for the Flask application
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db

config_name = os.getenv('FLASK_CONFIG', 'default')
print(f" * Starting app with config: {config_name}")

app = create_app(config_name)

# Log database configuration (without exposing credentials)
with app.app_context():
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite'):
        print(f" * Using database: SQLite")
    elif 'postgres' in db_uri:
        print(f" * Using database: PostgreSQL")
    else:
        print(f" * Using database: {db_uri.split(':')[0]}://...")

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
