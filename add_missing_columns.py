
import sqlite3

db_path = r"backend\jansevadb.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List of columns that might be missing (based on your model)
columns_to_add = [
    ("ai_category", "TEXT"),
    ("latitude", "FLOAT"),
    ("longitude", "FLOAT"),
    ("priority", "TEXT DEFAULT 'medium'"),
    ("sla_deadline", "TIMESTAMP"),
    ("updated_at", "TIMESTAMP"),
    ("resolved_at", "TIMESTAMP"),
    ("feedback_deadline", "TIMESTAMP"),
    ("feedback", "TEXT"),
    ("rating", "INTEGER"),
    ("is_overdue", "BOOLEAN DEFAULT 0"),
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}")
        print(f"✅ Added column: {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"ℹ️ Column {col_name} already exists – skipped")
        else:
            print(f"❌ Error adding {col_name}: {e}")

conn.commit()
conn.close()
print("\n✅ All missing columns processed.")
