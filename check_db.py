from backend.database import engine
from sqlalchemy import text

with engine.connect() as conn:

    result = conn.execute(
        text("""
        SELECT column_name, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'ratings'
        AND column_name = 'official_id'
        """)
    )

    print(list(result))