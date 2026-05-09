import sqlite3

# Path to your SQLite database
db_path = r"backend\jansevadb.sqlite"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE complaints ADD COLUMN is_emergency BOOLEAN DEFAULT 0")
    print("✅ Column 'is_emergency' added successfully!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Column 'is_emergency' already exists – no action needed.")
    else:
        print(f"❌ Error: {e}")

conn.commit()
conn.close()