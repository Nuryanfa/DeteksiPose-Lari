
import sqlite3
import os

def check():
    db_paths = ["backend/sql_app.db", "sql_app.db"]
    for path in db_paths:
        if os.path.exists(path):
            print(f"Checking {path}...")
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            try:
                cursor.execute("PRAGMA table_info(analysis_sessions)")
                columns = [info[1] for info in cursor.fetchall()]
                print(f"Columns in analysis_sessions: {columns}")
                if 'coach_notes' in columns:
                    print("✅ coach_notes exists.")
                else:
                    print("❌ coach_notes MISSING.")
            except Exception as e:
                print(f"Error: {e}")
            conn.close()
        else:
            print(f"❌ {path} not found.")

if __name__ == "__main__":
    check()
