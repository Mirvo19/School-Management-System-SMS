"""
Flask SMS - School Management System
Main application entry point
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    #login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.students import students_bp
    from app.routes.users import users_bp
    from app.routes.classes import classes_bp
    from app.routes.subjects import subjects_bp
    from app.routes.exams import exams_bp
    from app.routes.timetables import timetables_bp
    from app.routes.payments import payments_bp
    from app.routes.pins import pins_bp
    from app.routes.dorms import dorms_bp
    from app.routes.marks import marks_bp
    from app.routes.settings import settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(classes_bp, url_prefix='/classes')
    app.register_blueprint(subjects_bp, url_prefix='/subjects')
    app.register_blueprint(exams_bp, url_prefix='/exams')
    app.register_blueprint(timetables_bp, url_prefix='/timetables')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(pins_bp, url_prefix='/pins')
    app.register_blueprint(dorms_bp, url_prefix='/dorms')
    app.register_blueprint(marks_bp, url_prefix='/marks')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    #error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    #register template filters and context processors
    from app.utils.template_helpers import register_template_helpers
    register_template_helpers(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
