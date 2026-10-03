"""Safely migrate campusguard_logs.csv to the current schema.
The logger creates a .bak copy before changing an existing CSV schema.
Run from the project root: python fix_log.py
"""
from logger import ensure_log_file, LOG_FILE

if __name__ == "__main__":
    ensure_log_file()
    print(f"Log file checked: {LOG_FILE}")
    print("If a schema migration was needed, the original is saved as campusguard_logs.csv.bak")
