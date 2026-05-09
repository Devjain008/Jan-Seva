from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# ─────────────────────────────────────────────────────────────
# BASE DIRECTORY
# ─────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────
# SQLITE DATABASE PATH
# ─────────────────────────────────────────────────────────────

DB_PATH = os.path.join(BASE_DIR, "jansevadb.sqlite")

DATABASE_URL = f"sqlite:///{DB_PATH}"

# ─────────────────────────────────────────────────────────────
# SQLALCHEMY ENGINE
# ─────────────────────────────────────────────────────────────

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    pool_pre_ping=True
)

# ─────────────────────────────────────────────────────────────
# SESSION FACTORY
# ─────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ─────────────────────────────────────────────────────────────
# BASE MODEL CLASS
# ─────────────────────────────────────────────────────────────

Base = declarative_base()

# ─────────────────────────────────────────────────────────────
# DATABASE DEPENDENCY
# ─────────────────────────────────────────────────────────────

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()