import os
import re

env_path = '.env'

def force_fix():
    if not os.path.exists(env_path):
        print("No .env found")
        return

    with open(env_path, 'rb') as f: # Read binary to avoid encoding issues
        content = f.read().decode('utf-8', errors='ignore')

    lines = content.splitlines()
    new_lines = []
    
    found_url = False
    anon_key = None

    for line in lines:
        if line.startswith('SUPABASE_ANON_KEY='):
            # Already exists? keep it unless it's empty
            if len(line) > 20:
                anon_key = line.split('=')[1].strip()
            continue # We will add it at the end to be sure
            
        if line.startswith('SUPABASE_URL='):
            # Clean it
            # Regex to capture URL and potential trailing key
            # URL usually ends with .co or .in
            match = re.match(r'(SUPABASE_URL=https://[a-zA-Z0-9.-]+)(.*)', line)
            if match:
                url_part = match.group(1).strip()
                garbage = match.group(2).strip()
                
                new_lines.append(url_part)
                found_url = True
                
                if garbage and len(garbage) > 20:
                    # Attempt to recover key
                    # If it starts with lhdCI, it's missing the header eyJhbGci
                    # We can try to guess/prepend the standard header if it looks like a payload
                    if garbage.startswith('lhdCI'):
                        # Standard header for Supabase JWTs is usually eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
                        # concatenated with .
                        garbage = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + garbage
                    
                    anon_key = garbage
            else:
                new_lines.append(line)
        elif line.startswith('SUPABASE_KEY='):
             continue # Remove old key var
        else:
             new_lines.append(line)

    # Add key
    if anon_key:
        new_lines.append(f"SUPABASE_ANON_KEY={anon_key}")
    else:
        new_lines.append("SUPABASE_ANON_KEY=placeholder_replace_me")

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
        f.write('\n')
    
    print("Force fixed .env")

if __name__ == "__main__":
    force_fix()
