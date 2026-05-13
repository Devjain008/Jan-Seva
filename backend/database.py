from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE URL RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_database_url() -> tuple[str, bool]:
    """
    Returns:
        (database_url, is_postgres)

    Priority:
        1. PostgreSQL from Render DATABASE_URL
        2. SQLite fallback for localhost/dev
    """

    raw = os.environ.get("DATABASE_URL", "").strip()

    # ─────────────────────────────────────────
    # POSTGRESQL (RENDER / PRODUCTION)
    # ─────────────────────────────────────────

    if raw:

        # Fix old Render postgres:// issue
        if raw.startswith("postgres://"):

            raw = raw.replace(
                "postgres://",
                "postgresql://",
                1
            )

        # Add psycopg2 driver explicitly
        if raw.startswith("postgresql://"):

            raw = raw.replace(
                "postgresql://",
                "postgresql+psycopg2://",
                1
            )

        log.info(
            "✅ Using PostgreSQL database."
        )

        return raw, True

    # ─────────────────────────────────────────
    # SQLITE FALLBACK (LOCALHOST)
    # ─────────────────────────────────────────

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    sqlite_path = os.path.join(
        BASE_DIR,
        "jansevadb.sqlite"
    )

    sqlite_url = f"sqlite:///{sqlite_path}"

    log.warning(
        "⚠ DATABASE_URL not found. Falling back to SQLite."
    )

    return sqlite_url, False


DATABASE_URL, _IS_POSTGRES = _resolve_database_url()

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────────

if _IS_POSTGRES:

    engine = create_engine(

        DATABASE_URL,

        pool_pre_ping=True,

        pool_size=5,

        max_overflow=10,

        pool_recycle=280,

        pool_timeout=30,

        connect_args={

            "sslmode": "require",

            "connect_timeout": 10,

            "application_name": "jan-seva"
        },
    )

    log.info("✅ PostgreSQL engine initialized.")

else:

    engine = create_engine(

        DATABASE_URL,

        connect_args={
            "check_same_thread": False
        },

        pool_pre_ping=True
    )

    log.info("✅ SQLite engine initialized.")

# ─────────────────────────────────────────────────────────────────────────────
# SESSION FACTORY
# ─────────────────────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine,

    expire_on_commit=False
)

# ─────────────────────────────────────────────────────────────────────────────
# BASE MODEL
# ─────────────────────────────────────────────────────────────────────────────

Base = declarative_base()

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE DEPENDENCY
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:

        yield db

    except OperationalError as exc:

        log.warning(
            "⚠ DB OperationalError — retrying fresh connection: %s",
            exc
        )

        db.close()

        db = SessionLocal()

        yield db

    finally:

        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT MANAGER
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def db_session() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:

        yield db

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# CREATE TABLES
# ─────────────────────────────────────────────────────────────────────────────

def create_tables_if_missing() -> None:

    try:

        Base.metadata.create_all(
            bind=engine,
            checkfirst=True
        )

        log.info(
            "✅ Database tables verified/created."
        )

    except Exception as exc:

        log.error(
            "❌ Failed creating tables: %s",
            exc
        )

        raise

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

def db_ping() -> bool:

    try:

        with engine.connect() as conn:

            conn.execute(text("SELECT 1"))

        return True

    except Exception as exc:

        log.error(
            "❌ DB ping failed: %s",
            exc
        )

        return False

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE INFO
# ─────────────────────────────────────────────────────────────────────────────

def get_db_info() -> dict:

    try:

        with engine.connect() as conn:

            # ─────────────────────────────────
            # POSTGRESQL INFO
            # ─────────────────────────────────

            if _IS_POSTGRES:

                row = conn.execute(

                    text(
                        """
                        SELECT
                            current_database(),
                            current_user,
                            version(),
                            pg_size_pretty(
                                pg_database_size(current_database())
                            )
                        """
                    )

                ).fetchone()

                return {

                    "status": "ok",

                    "backend": "postgresql",

                    "database": row[0],

                    "user": row[1],

                    "version": row[2].split(",")[0],

                    "size": row[3]
                }

            # ─────────────────────────────────
            # SQLITE INFO
            # ─────────────────────────────────

            return {

                "status": "ok",

                "backend": "sqlite",

                "url": DATABASE_URL
            }

    except Exception as exc:

        return {

            "status": "error",

            "detail": str(exc)
        }