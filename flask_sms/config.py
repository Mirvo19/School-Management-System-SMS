"""
Configuration settings for Flask SMS application
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
print(f"Loading .env from: {env_path}")
if os.path.exists(env_path):
    print(".env file found!")
else:
    print(".env file NOT found!")
    
load_dotenv(env_path)
print(f"SUPABASE_URL loaded: {'Yes' if os.environ.get('SUPABASE_URL') else 'No'}")
print(f"SUPABASE_KEY loaded: {'Yes' if os.environ.get('SUPABASE_KEY') else 'No'}")
print(f"SUPABASE_ANON_KEY loaded: {'Yes' if os.environ.get('SUPABASE_ANON_KEY') else 'No'}")

if os.environ.get('SUPABASE_KEY'):
    print(f"SUPABASE_KEY start: {os.environ.get('SUPABASE_KEY')[:5]}...")
if os.environ.get('SUPABASE_ANON_KEY'):
    print(f"SUPABASE_ANON_KEY start: {os.environ.get('SUPABASE_ANON_KEY')[:5]}...")


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_RECORD_QUERIES = True
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
    # Support both SUPABASE_KEY and SUPABASE_ANON_KEY
    SUPABASE_KEY = (os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_ANON_KEY') or '').strip()
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTForms configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Application settings
    APP_NAME = 'School Management System'
    SCHOOL_NAME = os.environ.get('SCHOOL_NAME', 'Your School Name')
    SCHOOL_ACRONYM = os.environ.get('SCHOOL_ACRONYM', 'SMS')
    SCHOOL_CODE = os.environ.get('SCHOOL_CODE', 'SCH001')
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    # SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # uri = os.environ.get('DATABASE_URL')
    # if uri and uri.startswith('postgres://'):
    #     uri = uri.replace('postgres://', 'postgresql://', 1)
        
    # SQLALCHEMY_DATABASE_URI = uri
        
    SESSION_COOKIE_SECURE = True
    
    # Database connection options for stability
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     "pool_pre_ping": True,
    #     "pool_recycle": 300,
    # }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
