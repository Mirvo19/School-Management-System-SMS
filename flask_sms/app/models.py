from app import login_manager
from app.supabase_db import get_db, SupabaseModel

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    supabase = get_db()
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            return SupabaseModel(response.data[0])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# We can keep empty classes here if other files import them for type hints or constants,
# but ideally we should update imports to avoid dependency on this file.
# For now, I will clear the file to avoid ImportErrors related to 'db' which is now None.
