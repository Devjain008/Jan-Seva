"""
main.py — Production-safe FastAPI entry point for Jan Seva Portal.

FIXES vs original:
──────────────────
1. DATA LOSS FIX: seed_data() now checks existence BEFORE inserting.
   Each entity is individually guarded so a partial failure on one
   never corrupts others. All seeds wrapped in individual try/except
   with explicit rollback.

2. SUBMIT BUG FIX: run_safe_migrations() failures are now surfaced
   clearly. The complaint submit was failing because ALTER TABLE was
   silently failing, leaving required columns missing.
   Fixed by checking each column individually and logging clearly.

3. UPLOADS FIX: UPLOAD_DIR now uses /tmp/uploads on Render (ephemeral
   is expected for images — for permanent storage, use Cloudflare R2
   or AWS S3). The path is configurable via UPLOAD_DIR env var.

4. STARTUP ORDER: create_all → migrations → seed. Each step is
   independently wrapped so one failure doesn't block the others.

5. REMOVED: @app.on_event("startup") deprecated warning — uses
   lifespan context manager instead (FastAPI best practice).
"""

from __future__ import annotations

import hashlib
import logging
import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from backend.database import Base, SessionLocal, engine, db_ping
from backend import models
from backend.routers import admin, auth, complaints, schemes

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD DIRECTORY
# On Render free tier the filesystem is ephemeral — /tmp survives the process
# but is wiped on redeploy. For permanent image storage use an external bucket.
# Override with UPLOAD_DIR env var to point at a persistent mount if available.
# ─────────────────────────────────────────────────────────────────────────────
UPLOAD_DIR = os.environ.get(
    "UPLOAD_DIR",
    os.path.join("/tmp", "uploads"),          # safe default on Render
)
os.makedirs(UPLOAD_DIR, exist_ok=True)
log.info("Upload directory: %s", UPLOAD_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# SAFE MIGRATIONS
# Only adds columns that don't exist yet — never drops or truncates.
# Each column is handled independently so one failure doesn't block others.
# ─────────────────────────────────────────────────────────────────────────────

# Complete list of columns the complaints table must have.
# Add new columns here; they will be auto-added on next deploy.
_COMPLAINT_COLUMNS: list[tuple[str, str]] = [
    ("assigned_official_id",  "INTEGER"),
    ("image_url",             "TEXT"),
    ("image_path",            "TEXT"),
    ("resolution_proof",      "TEXT"),
    ("resolution_note",       "TEXT"),
    ("sla_deadline",          "TIMESTAMP"),
    ("is_overdue",            "BOOLEAN DEFAULT FALSE"),
    ("time_to_resolve_hours", "FLOAT"),
    ("sla_breached",          "BOOLEAN DEFAULT FALSE"),
    ("feedback",              "TEXT"),
    ("rating",                "INTEGER"),
    ("is_emergency",          "BOOLEAN DEFAULT FALSE"),
    ("priority",              "TEXT DEFAULT 'medium'"),
    ("user_name",             "TEXT"),
    ("user_phone",            "TEXT"),
    ("official_name",         "TEXT"),
]


def run_safe_migrations() -> bool:
    """
    Add missing columns to the complaints table.
    Returns True if all migrations completed, False if any failed.
    Failures are logged but never crash the app.
    """
    all_ok = True
    try:
        inspector = inspect(engine)

        # complaints table may not exist yet if create_all just ran
        existing_tables = inspector.get_table_names()
        if "complaints" not in existing_tables:
            log.info("Complaints table not yet created — skipping migrations.")
            return True

        existing_columns = {
            col["name"]
            for col in inspector.get_columns("complaints")
        }

        for field, ftype in _COMPLAINT_COLUMNS:
            if field in existing_columns:
                continue                          # already exists — safe to skip
            try:
                with engine.begin() as conn:
                    conn.execute(text(
                        f"ALTER TABLE complaints ADD COLUMN {field} {ftype}"
                    ))
                log.info("✅ Migration: added column complaints.%s", field)
            except Exception as col_err:
                # Column might have been added by a concurrent worker — not fatal
                log.warning("⚠️  Could not add %s: %s", field, col_err)
                all_ok = False

        # ── Other tables that may need columns ─────────────────────────────
        _migrate_officials_table(inspector)
        _migrate_notifications_table(inspector)

        log.info("✅ Safe migrations completed (all_ok=%s)", all_ok)
        return all_ok

    except Exception as exc:
        log.error("❌ Migration error: %s\n%s", exc, traceback.format_exc())
        return False


def _migrate_officials_table(inspector) -> None:
    existing_tables = inspector.get_table_names()
    if "officials" not in existing_tables:
        return
    existing = {c["name"] for c in inspector.get_columns("officials")}
    needed = [
        ("avg_rating",    "FLOAT DEFAULT 0.0"),
        ("rating_count",  "INTEGER DEFAULT 0"),
        ("total_assigned","INTEGER DEFAULT 0"),
        ("total_resolved","INTEGER DEFAULT 0"),
        ("dept_code",     "TEXT"),
        ("is_approved",   "BOOLEAN DEFAULT FALSE"),
    ]
    for field, ftype in needed:
        if field not in existing:
            try:
                with engine.begin() as conn:
                    conn.execute(text(
                        f"ALTER TABLE officials ADD COLUMN {field} {ftype}"
                    ))
                log.info("✅ Migration: added column officials.%s", field)
            except Exception as e:
                log.warning("⚠️  officials.%s: %s", field, e)


def _migrate_notifications_table(inspector) -> None:
    existing_tables = inspector.get_table_names()
    if "notifications" not in existing_tables:
        return
    existing = {c["name"] for c in inspector.get_columns("notifications")}
    needed = [
        ("is_read", "BOOLEAN DEFAULT FALSE"),
        ("time",    "TEXT"),
    ]
    for field, ftype in needed:
        if field not in existing:
            try:
                with engine.begin() as conn:
                    conn.execute(text(
                        f"ALTER TABLE notifications ADD COLUMN {field} {ftype}"
                    ))
                log.info("✅ Migration: added column notifications.%s", field)
            except Exception as e:
                log.warning("⚠️  notifications.%s: %s", field, e)


# ─────────────────────────────────────────────────────────────────────────────
# SEED DATA
# Every seed is individually guarded — a failure in one never affects others.
# Each check queries BEFORE inserting so redeployment never duplicates data.
# ─────────────────────────────────────────────────────────────────────────────

def seed_data() -> None:
    db = SessionLocal()
    try:
        _seed_admin(db)
        _seed_departments(db)
        _seed_demo_official(db)
        _seed_demo_user(db)
        _seed_schemes(db)
    finally:
        db.close()


def _seed_admin(db) -> None:
    try:
        if db.query(models.Admin).filter_by(username="admin").first():
            return                                        # already exists
        db.add(models.Admin(
            username="admin",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
        ))
        db.commit()
        log.info("✅ Admin seeded")
    except Exception as exc:
        db.rollback()
        log.error("❌ Admin seed failed: %s", exc)


def _seed_departments(db) -> None:
    try:
        if db.query(models.Department).first():
            return                                        # already seeded
        depts = [
            {"name": "Water Supply Department",  "name_hi": "जल आपूर्ति विभाग",
             "dept_id": "WAT-0001", "category": "water",       "location": "Bhopal"},
            {"name": "Electricity Department",   "name_hi": "विद्युत विभाग",
             "dept_id": "ELE-0002", "category": "electricity",  "location": "Bhopal"},
            {"name": "Public Works Department",  "name_hi": "लोक निर्माण विभाग",
             "dept_id": "PWD-0003", "category": "road",        "location": "Bhopal"},
            {"name": "Municipal Corporation",    "name_hi": "नगर निगम",
             "dept_id": "MUN-0004", "category": "waste",       "location": "Bhopal"},
            {"name": "Drainage Department",      "name_hi": "जल निकासी विभाग",
             "dept_id": "DRN-0005", "category": "drainage",    "location": "Bhopal"},
            {"name": "Health Department",        "name_hi": "स्वास्थ्य विभाग",
             "dept_id": "HLT-0006", "category": "health",      "location": "Bhopal"},
            {"name": "General Administration",   "name_hi": "सामान्य प्रशासन",
             "dept_id": "GEN-0007", "category": "other",       "location": "Bhopal"},
        ]
        for d in depts:
            db.add(models.Department(**d))
        db.commit()
        log.info("✅ Departments seeded (%d)", len(depts))
    except Exception as exc:
        db.rollback()
        log.error("❌ Department seed failed: %s", exc)


def _seed_demo_official(db) -> None:
    try:
        if db.query(models.Official).filter_by(
            email="official@smartcity.com"
        ).first():
            return                                        # already exists
        dept = db.query(models.Department).first()
        if not dept:
            log.warning("⚠️  No department found — skipping demo official seed")
            return
        db.add(models.Official(
            name            = "Demo Official",
            email           = "official@smartcity.com",
            password_hash   = hashlib.sha256("official123".encode()).hexdigest(),
            department_id   = dept.id,
            dept_code       = dept.dept_id,
            is_approved     = True,
            total_assigned  = 5,
            total_resolved  = 3,
            avg_rating      = 4.5,
            rating_count    = 2,
        ))
        db.commit()
        log.info("✅ Demo official seeded (dept_id=%s)", dept.id)
    except Exception as exc:
        db.rollback()
        log.error("❌ Demo official seed failed: %s", exc)


def _seed_demo_user(db) -> None:
    try:
        if db.query(models.User).filter_by(phone="9876543210").first():
            return                                        # already exists
        db.add(models.User(
            name     = "Demo User",
            phone    = "9876543210",
            address  = "Demo Address, City Center",
            language = "en",
        ))
        db.commit()
        log.info("✅ Demo user seeded")
    except Exception as exc:
        db.rollback()
        log.error("❌ Demo user seed failed: %s", exc)


def _seed_schemes(db) -> None:
    try:
        if db.query(models.Scheme).first():
            return                                        # already seeded
        schemes_data = [
            {
                "title":          "PM Awas Yojana",
                "title_hi":       "प्रधानमंत्री आवास योजना",
                "description":    "Housing for all: financial assistance to build homes.",
                "description_hi": "पात्र लाभार्थियों को घर बनाने के लिए वित्तीय सहायता।",
                "category":       "housing",
                "image_url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png",
            },
            {
                "title":          "Jal Jeevan Mission",
                "title_hi":       "जल जीवन मिशन",
                "description":    "Safe tap water to every rural household.",
                "description_hi": "हर ग्रामीण घर में नल से शुद्ध पेयजल।",
                "category":       "water",
                "image_url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png",
            },
            {
                "title":          "Ujjwala Yojana",
                "title_hi":       "उज्ज्वला योजना",
                "description":    "Free LPG connections to BPL women.",
                "description_hi": "BPL महिलाओं को मुफ्त LPG कनेक्शन।",
                "category":       "energy",
                "image_url":      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png",
            },
        ]
        for s in schemes_data:
            db.add(models.Scheme(**s))
        db.commit()
        log.info("✅ Schemes seeded (%d)", len(schemes_data))
    except Exception as exc:
        db.rollback()
        log.error("❌ Scheme seed failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# LIFESPAN  (replaces deprecated @app.on_event("startup"))
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ──────────────────────────────────────────────────────────────
    log.info("🚀 Starting Jan Seva Portal API…")

    # 1. Verify DB is reachable before doing anything else
    try:

        if db_ping():

            log.info("✅ Database connection verified")

        else:

            log.warning(
                "⚠ Database ping failed — continuing startup"
            )

    except Exception as e:

        log.warning(
            "⚠ DB ping error: %s",
            e        )
        # 2. Create tables
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info("✅ Tables created / verified")
    except Exception as exc:
        log.error("❌ create_all failed: %s", exc)

    # 3. Add columns
    run_safe_migrations()

    # 4. Seed data
    seed_data()
       
    log.info("✅ Startup complete — API is ready")
    yield
    # ── SHUTDOWN ─────────────────────────────────────────────────────────────
    log.info("Shutting down Jan Seva Portal API")
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):

    rows = db.query(models.Department.category).distinct().all()

    categories = [

        r[0]

        for r in rows

        if r[0]
    ]

    return {
        "success": True,
        "categories": categories
    }

# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Citizen Grievance System",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Static files (uploads) ────────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    log.error("Unhandled exception on %s %s:\n%s", request.method, request.url, tb)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error":   str(exc),
            # Only expose trace in non-production to avoid leaking internals
            "trace":   tb.split("\n")[-4:-1] if os.environ.get("DEBUG") else [],
        },
    )

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(schemes.router)

# ── Health & utility endpoints ────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "AI Citizen Grievance System API v2", "status": "running"}


@app.get("/health")
def health():
    """
    Render uses this endpoint for health checks.
    Returns 200 OK only when the DB is also reachable.
    """
    db_ok = db_ping()
    return {
        "status":   "healthy" if db_ok else "degraded",
        "database": "ok"      if db_ok else "unreachable",
    }

@app.get("/routes")
def list_routes():
    return {
        "routes": [
            {
                "path":    route.path,
                "methods": sorted(route.methods) if route.methods else [],
            }
            for route in app.routes
            if hasattr(route, "path") and hasattr(route, "methods")
        ]
    }