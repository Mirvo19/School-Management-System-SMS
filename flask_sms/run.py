"""
Run script for the Flask application
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

config_name = os.getenv('FLASK_CONFIG', 'default')
print(f" * Starting app with config: {config_name}")

app = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
