from app import login_manager
from app.supabase_db import get_db, SupabaseModel

class User(SupabaseModel):
    """
    User model class extending the generic SupabaseModel.
    Adds application-specific helper methods for roles.
    """
    def __init__(self, data):
        super().__init__(data)
    
    def is_admin(self):
        """Check if user has admin privileges (admin or super_admin)"""
        return self.user_type in ['super_admin', 'admin']

    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.user_type == 'super_admin'

    def is_teacher(self):
        """Check if user is a teacher"""
        return self.user_type == 'teacher'

    def is_student(self):
        """Check if user is a student"""
        return self.user_type == 'student'

    def is_parent(self):
        """Check if user is a parent"""
        return self.user_type == 'parent'

    def is_accountant(self):
        """Check if user is an accountant"""
        return self.user_type == 'accountant'
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.user_type == role_name

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    supabase = get_db()
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            return User(response.data[0])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

# We can keep empty classes here if other files import them for type hints or constants,
# but ideally we should update imports to avoid dependency on this file.
# For now, I will clear the file to avoid ImportErrors related to 'db' which is now None.
