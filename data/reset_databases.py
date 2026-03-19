import os
import shutil
from pathlib import Path

def reset_databases():
    data_root = Path(__file__).parent
    print(f"[*] Scanning {data_root} for database files...")
    
    db_files = list(data_root.glob("**/*.db"))
    
    if not db_files:
        print("[!] No .db files found.")
        return

    for db_file in db_files:
        try:
            print(f"[-] Deleting {db_file}...")
            os.remove(db_file)
        except Exception as e:
            print(f"[ERROR] Failed to delete {db_file}: {e}")

    print("[+] All database files removed.")
    print("[*] To recreate them with fresh schemas, simply restart the backend application.")

if __name__ == "__main__":
    reset_databases()
