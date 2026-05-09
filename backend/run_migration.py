# run_migration.py - Run this file directly
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import engine
from sqlalchemy import text, inspect

def run_migration():
    print("Starting database migration...")
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Create SLA policies table
        if "sla_policies" not in tables:
            print("Creating sla_policies table...")
            conn.execute(text("""
                CREATE TABLE sla_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category VARCHAR(50) NOT NULL UNIQUE,
                    hours_to_resolve INTEGER NOT NULL,
                    priority_multiplier FLOAT DEFAULT 1.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert default SLA policies
            default_slas = [
                ("water", 24),
                ("electricity", 24),
                ("road", 72),
                ("waste", 48),
                ("drainage", 48),
                ("health", 36),
                ("other", 72),
            ]
            for cat, hours in default_slas:
                conn.execute(text(f"""
                    INSERT OR IGNORE INTO sla_policies (category, hours_to_resolve, priority_multiplier)
                    VALUES ('{cat}', {hours}, 1.0)
                """))
            print("✓ SLA policies table created")
        
        # Add columns to complaints table
        if 'complaints' in tables:
            columns = [col['name'] for col in inspector.get_columns('complaints')]
            
            sla_columns = [
                ("sla_deadline", "TIMESTAMP"),
                ("is_overdue", "BOOLEAN DEFAULT 0"),
                ("time_to_resolve_hours", "FLOAT"),
                ("SLA_breached", "BOOLEAN DEFAULT 0")
            ]
            
            for col_name, col_def in sla_columns:
                if col_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_def}"))
                        print(f"✓ Added column: {col_name}")
                    except Exception as e:
                        print(f"Note: {col_name} - {e}")
    
    print("Migration completed!")

if __name__ == "__main__":
    run_migration()
    print("\n✅ Migration done! Now restart your backend server.")