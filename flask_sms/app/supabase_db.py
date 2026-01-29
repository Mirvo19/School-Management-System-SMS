import os
from supabase import create_client, Client

# Fetch and clean environment variables
url_raw = os.environ.get("SUPABASE_URL", "")
url: str = url_raw.strip().strip("'").strip('"')

# Prefer ANON key, fallback to generic KEY
key_raw = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
key: str = key_raw.strip().strip("'").strip('"') if key_raw else None

if not url:
    print("WARNING: SUPABASE_URL not found or empty (supabase_db.py)")
else:
    # Log valid URL format for debugging
    print(f"Supabase Client init using URL: {url} (Length: {len(url)})")
    if "postgres://" in url or "postgresql://" in url:
        print("CRITICAL ERROR: SUPABASE_URL looks like a database connection string, not an API URL!")
        print("Please use the 'Project URL' from Supabase Settings -> API (e.g., https://xyz.supabase.co)")

if not key:
    print("WARNING: SUPABASE_KEY/SUPABASE_ANON_KEY not found or empty (supabase_db.py)")
else:
    print(f"Supabase Client init using key starting with: {key[:10]}... (Length: {len(key)})")
    
    # Diagnostic: Check if key looks like a JWT (starts with 'ey')
    if not key.startswith("ey"):
        print(f"CRITICAL WARNING: The Supabase Key does NOT start with 'ey'.")
        print("Did you paste the 'JWT Secret' instead of the 'anon'/'service_role' key?")
    elif key.count('.') != 2:
        print(f"CRITICAL WARNING: The Supabase Key seems malformed.")
        print(f"It contains {key.count('.')} dots ('.') instead of 2. A valid JWT must have 3 parts separated by dots.")
        print("Your key is likely TRUNCATED (cut off). Please copy the full key again.")
    elif len(key) < 150:
        print(f"WARNING: The Supabase Key length ({len(key)}) seems suspiciously short for a JWT.")
        print("Please double check that you copied the ENTIRE key.")
        print("Or maybe check for accidentally pasted variables?")
    else:
        print(f"Supabase Client init using key starting with: {key[:5]}...")

# Initialize client only if env vars exist (to avoid circular import errors during setup)
supabase: Client = create_client(url, key) if url and key else None

def get_db():
    """Get the Supabase client instance"""
    if not supabase:
        # Fallback or re-attempt if env vars were loaded late
        current_url = os.environ.get("SUPABASE_URL")
        current_key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")
        
        if not current_url:
            print("ERROR: SUPABASE_URL is missing from environment.")
        if not current_key:
            print("ERROR: SUPABASE_ANON_KEY and SUPABASE_KEY are missing from environment.")
            
        if current_url and current_key:
            return create_client(current_url, current_key)
        raise Exception("Supabase credentials not found in environment")
    return supabase

class SupabaseModel:
    """
    Wrapper for Supabase dictionary responses to allow object-attribute access.
    Compatible with Jinja2 templates expecting user.name, etc.
    """
    def __init__(self, data):
        self._data = data
        if data:
            for key, value in data.items():
                # If value is a dict, it might be a relationship -> wrap it too?
                # For now, keep it simple. If we need deep wrapping, we can add it.
                setattr(self, key, value)
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    @classmethod
    def from_list(cls, data_list):
        """Convert a list of dictionaries to a list of SupabaseModels"""
        return [cls(item) for item in data_list] if data_list else []
    
    # Flask-Login required mixin methods
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
