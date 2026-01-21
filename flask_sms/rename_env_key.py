import os

env_path = '.env'

def rename_key():
    if not os.path.exists(env_path):
        print(f"{env_path} not found.")
        return

    with open(env_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    renamed = False

    for line in lines:
        if line.startswith('SUPABASE_KEY='):
            new_lines.append(line.replace('SUPABASE_KEY=', 'SUPABASE_ANON_KEY='))
            renamed = True
        else:
            new_lines.append(line)

    if renamed:
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        print("Renamed SUPABASE_KEY to SUPABASE_ANON_KEY in .env")
    else:
        print("SUPABASE_KEY not found or already renamed.")

if __name__ == "__main__":
    rename_key()
