import os

env_path = '.env'

def fix_env():
    if not os.path.exists(env_path):
        print(f"{env_path} not found.")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    supabase_key_found = False
    extracted_key = None

    for line in lines:
        if line.startswith('SUPABASE_URL='):
            # Split by whitespace
            parts = line.strip().split(None, 1) # Split on first whitespace sequence
            # parts[0] is 'SUPABASE_URL=http://...'
            # actually split on '=' first
            key, val = line.split('=', 1)
            val = val.strip()
            
            # Check if val has spaces
            if ' ' in val or '\t' in val:
                url_parts = val.split()
                clean_url = url_parts[0]
                possible_key = url_parts[-1] if len(url_parts) > 1 else None
                
                new_lines.append(f"SUPABASE_URL={clean_url}\n")
                if possible_key and len(possible_key) > 20: # simple heuristic
                    extracted_key = possible_key
            else:
                new_lines.append(line)
        elif line.startswith('SUPABASE_KEY='):
            supabase_key_found = True
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Append extracted key if SUPABASE_KEY is missing
    if extracted_key and not supabase_key_found:
        new_lines.append(f"SUPABASE_KEY={extracted_key}\n")
        print(f"Extracted and added SUPABASE_KEY: {extracted_key[:10]}...")

    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    print("Fixed .env file.")

if __name__ == "__main__":
    fix_env()
