"""
Template filters and context processors
"""
from flask import current_app
from datetime import datetime


def register_template_helpers(app):
    """Register template filters and context processors"""
    
    @app.template_filter('format_date')
    def format_date_filter(date, format='%Y-%m-%d'):
        """Format date for display"""
        if date:
            return date.strftime(format)
        return ''
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(dt, format='%Y-%m-%d %H:%M:%S'):
        """Format datetime for display"""
        if dt:
            return dt.strftime(format)
        return ''
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context"""
        def get_app_name():
            return current_app.config.get('APP_NAME', 'SMS')
        
        def get_school_name():
            return current_app.config.get('SCHOOL_NAME', 'School')
        
        def current_time_str():
            return datetime.now().strftime('%d/%m/%Y')

        return dict(
            get_app_name=get_app_name,
            get_school_name=get_school_name,
            current_time_str=current_time_str
        )
