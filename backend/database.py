

from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker, Session

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# URL RESOLUTION
# Render sets DATABASE_URL as  postgres://user:pass@host:5432/dbname
# SQLAlchemy 2.x needs        postgresql+psycopg2://user:pass@host:5432/dbname
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_database_url() -> tuple[str, bool]:
    """
    Returns (url, is_postgres).
    Raises RuntimeError in production if DATABASE_URL is missing.
    """
    raw = os.environ.get("DATABASE_URL", "").strip()

    if raw:
        # Step 1 — normalise the scheme
        if raw.startswith("postgres://"):
            raw = raw.replace("postgres://", "postgresql://", 1)

        # Step 2 — add explicit psycopg2 driver if bare postgresql:// is given
        # This prevents "Can't load plugin: sqlalchemy.dialects:postgresql"
        # on some SQLAlchemy 2.x / psycopg2 combinations.
        if raw.startswith("postgresql://"):
            raw = raw.replace("postgresql://", "postgresql+psycopg2://", 1)

        # Already has driver specified — leave as-is
        log.info("Using PostgreSQL: %s", raw.split("@")[-1])  # log host only, not creds
        return raw, True

    # ── No DATABASE_URL ───────────────────────────────────────────────────────
    
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )


DATABASE_URL, _IS_POSTGRES = _resolve_database_url()

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# pool_recycle=280 → recycle connections before Render's 300s idle timeout kills
#                    them (prevents "SSL connection has been closed unexpectedly")
# pool_pre_ping=True → test connection health before handing it to a request
# pool_timeout=30 → don't wait more than 30s for a pool slot (fail fast)
# ─────────────────────────────────────────────────────────────────────────────

if _IS_POSTGRES:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,      # re-validate before use
        pool_size=5,             # persistent connections kept open
        max_overflow=10,         # extra connections under burst load
        pool_recycle=280,        # FIX: recycle before Render's 300s timeout
        pool_timeout=30,         # fail fast if pool is exhausted
        connect_args={
            "sslmode": "require",             # FIX: Render requires SSL
            "connect_timeout": 10,            # don't hang on network issues
            "application_name": "jan-seva",  # visible in pg_stat_activity
        },
    )
else:
    # SQLite — local dev only
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# SESSION FACTORY & BASE
# ─────────────────────────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # avoids lazy-load errors after commit in async contexts
)

Base = declarative_base()

# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCY  (FastAPI / Flask / plain usage)
# FIX: retries once on OperationalError (stale pool connection after Render
# sleep) before propagating, eliminating cold-start 503s.
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session; close it when the request finishes.
    Use as a FastAPI dependency:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as exc:
        log.warning("DB OperationalError — retrying with fresh connection: %s", exc)
        db.close()
        db = SessionLocal()
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context-manager version for use outside of request cycles:
        with db_session() as db:
            db.query(...)
    """
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
# STARTUP HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def create_tables_if_missing() -> None:
    """
    CREATE TABLE IF NOT EXISTS for every model that inherits from Base.

    SAFE: SQLAlchemy's create_all() maps to CREATE TABLE IF NOT EXISTS —
    it never drops, truncates, or alters existing tables or data.

    Call this ONCE at application startup (in main.py / app startup event).
    For schema changes use Alembic migrations instead.
    """
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info("Database tables verified / created.")
    except Exception as exc:
        log.error("Failed to create tables: %s", exc)
        raise


def db_ping() -> bool:
    """
    Lightweight health check — returns True if the DB is reachable.
    Use in your /health or /readyz endpoint.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        log.error("DB ping failed: %s", exc)
        return False


def get_db_info() -> dict:
    """
    Returns connection metadata useful for debugging on Render.
    Safe to expose on an internal /debug endpoint (not public).
    """
    try:
        with engine.connect() as conn:
            if _IS_POSTGRES:
                row = conn.execute(text(
                    "SELECT current_database(), current_user, "
                    "version(), pg_size_pretty(pg_database_size(current_database()))"
                )).fetchone()
                return {
                    "status": "ok",
                    "backend": "postgresql",
                    "database": row[0],
                    "user":     row[1],
                    "version":  row[2].split(",")[0],
                    "size":     row[3],
                }
            else:
                return {"status": "ok", "backend": "sqlite", "url": DATABASE_URL}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}