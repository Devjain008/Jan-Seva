from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# ─────────────────────────────────────────────────────────────
# DATABASE URL RESOLUTION
#
# Priority order:
#   1. DATABASE_URL env var  →  PostgreSQL on Render (production)
#   2. SQLITE_PATH env var   →  Render Persistent Disk path
#   3. Fallback              →  Local dev (backend/jansevadb.sqlite)
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_URL = os.environ.get("DATABASE_URL")   # Set by Render PostgreSQL

if DATABASE_URL:
    # ── PostgreSQL (Render managed DB) ──────────────────────
    # Render still injects "postgres://" in older plans;
    # SQLAlchemy 1.4+ requires "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    DB_TYPE = "postgresql"

else:
    # ── SQLite (local dev OR Render Persistent Disk) ────────
    SQLITE_PATH = os.environ.get(
        "SQLITE_PATH",
        os.path.join(BASE_DIR, "jansevadb.sqlite")   # local dev default
    )

    # Ensure the directory exists (important for /data mount on Render)
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    DB_TYPE = "sqlite"

# ─────────────────────────────────────────────────────────────
# SESSION FACTORY
# ─────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─────────────────────────────────────────────────────────────
# BASE MODEL CLASS
# ─────────────────────────────────────────────────────────────

Base = declarative_base()

# ─────────────────────────────────────────────────────────────
# DATABASE DEPENDENCY  (FastAPI / route injection)
# ─────────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────
# HEALTH CHECK  (optional — useful for startup verification)
# ─────────────────────────────────────────────────────────────

def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        return False