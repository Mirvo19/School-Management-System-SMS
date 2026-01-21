#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database and seed it
# python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
# Run seeder
# python seed.py
