# backend/fix_missing_columns.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "jansevadb.sqlite")

# All columns that should exist in the `complaints` table (based on models.Complaint)
EXPECTED_COLUMNS = {
    "ai_category": "TEXT",
    "latitude": "FLOAT",
    "longitude": "FLOAT",
    "priority": "TEXT DEFAULT 'medium'",
    "sla_deadline": "TIMESTAMP",
    "updated_at": "TIMESTAMP",
    "resolved_at": "TIMESTAMP",
    "feedback_deadline": "TIMESTAMP",
    "feedback": "TEXT",
    "rating": "INTEGER",
    "is_overdue": "BOOLEAN DEFAULT 0",
    "is_emergency": "BOOLEAN DEFAULT 0",          # ← critical missing column
    "image_path": "VARCHAR(500)",
    "time_to_resolve_hours": "FLOAT",
    "SLA_breached": "BOOLEAN DEFAULT 0",
}

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(complaints)")
    existing = {row[1] for row in cursor.fetchall()}

    added = []
    for col, col_type in EXPECTED_COLUMNS.items():
        if col not in existing:
            try:
                cursor.execute(f"ALTER TABLE complaints ADD COLUMN {col} {col_type}")
                added.append(col)
                print(f"✅ Added column: {col}")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Could not add {col}: {e}")

    if added:
        conn.commit()
        print(f"\n🎉 Added {len(added)} column(s): {', '.join(added)}")
        print("▶️ Restart your backend server now.")
    else:
        print("ℹ️ All required columns already exist. No changes made.")

    conn.close()

if __name__ == "__main__":
    run_migration()