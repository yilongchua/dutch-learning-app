import os
import shutil
import json
import time
from pathlib import Path

def reset_databases():
    data_root = Path(__file__).parent
    print(f"[*] Scanning {data_root} for database files...")
    
    db_files = list(data_root.glob("**/*.db"))
    
    if not db_files:
        print("[!] No .db files found.")
    else:
        for db_file in db_files:
            try:
                print(f"[-] Deleting {db_file}...")
                os.remove(db_file)
            except Exception as e:
                print(f"[ERROR] Failed to delete {db_file}: {e}")
        print("[+] All database files removed.")

    # Write a timestamp to the frontend's public folder
    try:
        frontend_public = data_root.parent / 'frontend' / 'public'
        version_file = frontend_public / 'db_version.json'
        version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(version_file, 'w') as f:
            json.dump({"last_reset": time.time()}, f)
        print(f"[+] Notified frontend to clear state (via {version_file.name}).")
    except Exception as e:
        print(f"[ERROR] Failed to notify frontend: {e}")

    print("[*] To recreate them with fresh schemas, simply restart the backend application.")

if __name__ == "__main__":
    reset_databases()
