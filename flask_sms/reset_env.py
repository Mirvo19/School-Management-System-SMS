import os

env_content = """# Flask configuration
SECRET_KEY=dev-secret-key
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Supabase Keys
SUPABASE_URL=https://veywqpxgueihhatwbwpi.supabase.co
# TODO: Paste your Anon Public Key below
SUPABASE_ANON_KEY=paste_your_anon_key_here

# School settings
SCHOOL_NAME=My School
SCHOOL_ACRONYM=SMS
SCHOOL_CODE=SCH001
"""

with open('.env', 'w') as f:
    f.write(env_content)
    
print(".env file has been reset.")
