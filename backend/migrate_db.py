# backend/migrate_db.py
from database import engine
from sqlalchemy import text, inspect

def run_migration():
    print("Starting database migration...")
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # ─────────────────────────────────────────────────────────────
        # 1. Create sla_policies table (if missing)
        # ─────────────────────────────────────────────────────────────
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
                ("water", 24, 1.0),
                ("electricity", 24, 1.0),
                ("road", 72, 1.0),
                ("waste", 48, 1.0),
                ("drainage", 48, 1.0),
                ("health", 36, 1.0),
                ("other", 72, 1.0),
            ]
            for cat, hours, multiplier in default_slas:
                conn.execute(text(f"""
                    INSERT INTO sla_policies (category, hours_to_resolve, priority_multiplier)
                    VALUES ('{cat}', {hours}, {multiplier})
                """))
            print("✓ sla_policies table created with default policies")
        else:
            print("✓ sla_policies table already exists")
        
        # ─────────────────────────────────────────────────────────────
        # 2. Add SLA columns to complaints table (if missing)
        # ─────────────────────────────────────────────────────────────
        # Refresh column list
        inspector = inspect(engine)
        columns = inspector.get_columns('complaints')
        column_names = [col['name'] for col in columns]
        
        sla_columns = [
            ("sla_deadline", "TIMESTAMP"),
            ("is_overdue", "BOOLEAN DEFAULT 0"),
            ("time_to_resolve_hours", "FLOAT"),
            ("SLA_breached", "BOOLEAN DEFAULT 0")
        ]
        for col_name, col_def in sla_columns:
            if col_name not in column_names:
                print(f"Adding column {col_name} to complaints...")
                try:
                    conn.execute(text(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_def}"))
                    print(f"✓ Column {col_name} added")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"✓ Column {col_name} already exists")
        
        # ─────────────────────────────────────────────────────────────
        # 3. Add image_path column (for complaint images)
        # ─────────────────────────────────────────────────────────────
        # Refresh column list again (in case SLA columns were just added)
        inspector = inspect(engine)
        columns = inspector.get_columns('complaints')
        column_names = [col['name'] for col in columns]
        
        if "image_path" not in column_names:
            print("Adding column image_path to complaints...")
            try:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN image_path VARCHAR(500)"))
                print("✓ Column image_path added")
            except Exception as e:
                print(f"Error adding image_path: {e}")
        else:
            print("✓ Column image_path already exists")
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()