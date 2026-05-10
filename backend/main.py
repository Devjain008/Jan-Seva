from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.database import engine, Base, SessionLocal
from backend import models
from backend.routers import auth, complaints, admin, schemes

from sqlalchemy import inspect, text

import hashlib
import traceback
import os

# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="AI Citizen Grievance System",
    version="2.0.0"
)

# ─────────────────────────────────────────────
# UPLOAD DIRECTORY
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "../uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────────
# GLOBAL ERROR HANDLER
# ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    error_details = traceback.format_exc()

    print(f"ERROR: {error_details}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )

# ─────────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(schemes.router)

# ─────────────────────────────────────────────
# SAFE DATABASE MIGRATIONS
# ─────────────────────────────────────────────

def run_migrations():

    try:

        inspector = inspect(engine)

        cols = inspector.get_columns("complaints")

        col_names = {c["name"] for c in cols}

        missing_columns = {

            "assigned_official_id": "INTEGER",
            "image_url": "TEXT",
            "resolution_proof": "TEXT",
            "resolution_note": "TEXT",

            "sla_deadline": "TIMESTAMP",
            "is_overdue": "BOOLEAN DEFAULT FALSE",
            "time_to_resolve_hours": "FLOAT",
            "SLA_breached": "BOOLEAN DEFAULT FALSE"
        }

        with engine.begin() as conn:

            for col, col_type in missing_columns.items():

                if col not in col_names:

                    try:

                        conn.execute(
                            text(
                                f'ALTER TABLE complaints ADD COLUMN "{col}" {col_type}'
                            )
                        )

                        print(f"✅ Added column: {col}")

                    except Exception as e:

                        print(f"⚠️ Migration skipped for {col}: {e}")

    except Exception as e:

        print(f"❌ Migration error: {e}")

# ─────────────────────────────────────────────
# SAFE SEED DATA
# ─────────────────────────────────────────────

def seed_data():

    db = SessionLocal()

    try:

        # ─────────────────────────
        # ADMIN
        # ─────────────────────────

        existing_admin = db.query(models.Admin).filter(
            models.Admin.username == "admin"
        ).first()

        if not existing_admin:

            admin_user = models.Admin(
                username="admin",
                password_hash=hashlib.sha256(
                    "admin123".encode()
                ).hexdigest()
            )

            db.add(admin_user)

            db.commit()

            print("✅ Admin created")

        # ─────────────────────────
        # DEPARTMENTS
        # ─────────────────────────

        departments = [

            {
                "name":"Water Supply Department",
                "name_hi":"जल आपूर्ति विभाग",
                "dept_id":"WAT-0001",
                "category":"water",
                "location":"Bhopal"
            },

            {
                "name":"Electricity Department",
                "name_hi":"विद्युत विभाग",
                "dept_id":"ELE-0002",
                "category":"electricity",
                "location":"Bhopal"
            },

            {
                "name":"Public Works Department",
                "name_hi":"लोक निर्माण विभाग",
                "dept_id":"PWD-0003",
                "category":"road",
                "location":"Bhopal"
            },

            {
                "name":"Municipal Corporation",
                "name_hi":"नगर निगम",
                "dept_id":"MUN-0004",
                "category":"waste",
                "location":"Bhopal"
            },

            {
                "name":"Drainage Department",
                "name_hi":"जल निकासी विभाग",
                "dept_id":"DRN-0005",
                "category":"drainage",
                "location":"Bhopal"
            },

            {
                "name":"Health Department",
                "name_hi":"स्वास्थ्य विभाग",
                "dept_id":"HLT-0006",
                "category":"health",
                "location":"Bhopal"
            },

            {
                "name":"General Administration",
                "name_hi":"सामान्य प्रशासन",
                "dept_id":"GEN-0007",
                "category":"other",
                "location":"Bhopal"
            }

        ]

        for d in departments:

            existing = db.query(models.Department).filter(
                models.Department.dept_id == d["dept_id"]
            ).first()

            if not existing:

                db.add(models.Department(**d))

        db.commit()

        print("✅ Departments verified")

        # ─────────────────────────
        # DEMO OFFICIAL
        # ─────────────────────────

        existing_official = db.query(models.Official).filter(
            models.Official.email == "official@smartcity.com"
        ).first()

        if not existing_official:

            dept = db.query(models.Department).filter(
                models.Department.dept_id == "WAT-0001"
            ).first()

            if dept:

                official = models.Official(
                    name="Demo Official",
                    email="official@smartcity.com",
                    password_hash=hashlib.sha256(
                        "official123".encode()
                    ).hexdigest(),
                    department_id=dept.id,
                    dept_code=dept.dept_id,
                    is_approved=True,
                    total_assigned=5,
                    total_resolved=3,
                    avg_rating=4.5,
                    rating_count=2
                )

                db.add(official)

                db.commit()

                print("✅ Demo Official created")

        # ─────────────────────────
        # DEMO USER
        # ─────────────────────────

        existing_user = db.query(models.User).filter(
            models.User.phone == "9876543210"
        ).first()

        if not existing_user:

            user = models.User(
                name="Demo User",
                phone="9876543210",
                address="Demo Address",
                language="en"
            )

            db.add(user)

            db.commit()

            print("✅ Demo User created")

        # ─────────────────────────
        # SCHEMES
        # ─────────────────────────

        schemes_data = [

            {
                "title":"PM Awas Yojana",
                "title_hi":"प्रधानमंत्री आवास योजना",
                "description":"Housing assistance scheme.",
                "description_hi":"आवास सहायता योजना।",
                "category":"housing",
                "image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png"
            },

            {
                "title":"Jal Jeevan Mission",
                "title_hi":"जल जीवन मिशन",
                "description":"Safe drinking water scheme.",
                "description_hi":"सुरक्षित पेयजल योजना।",
                "category":"water",
                "image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png"
            }

        ]

        for s in schemes_data:

            existing = db.query(models.Scheme).filter(
                models.Scheme.title == s["title"]
            ).first()

            if not existing:

                db.add(models.Scheme(**s))

        db.commit()

        print("✅ Schemes verified")

    except Exception as e:

        print(f"❌ Seed Error: {e}")

        traceback.print_exc()

    finally:

        db.close()

# ─────────────────────────────────────────────
# STARTUP EVENT
# ─────────────────────────────────────────────

@app.on_event("startup")
async def startup():

    try:

        Base.metadata.create_all(bind=engine)

        run_migrations()

        db = SessionLocal()

        try:

            has_admin = db.query(models.Admin).first()

            if not has_admin:

                print("🌱 First-time setup running...")

                seed_data()

            else:

                print("✅ Existing database detected")

        finally:

            db.close()

        print("✅ Startup completed safely")

    except Exception as e:

        print(f"❌ Startup error: {e}")

        traceback.print_exc()

# ─────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────

@app.get("/")
def root():

    return {
        "message": "AI Citizen Grievance System API v2",
        "status": "running"
    }

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

# ─────────────────────────────────────────────
# ROUTES LIST
# ─────────────────────────────────────────────

@app.get("/routes")
def list_routes():

    routes = []

    for route in app.routes:

        if hasattr(route, "path") and hasattr(route, "methods"):

            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })

    return {
        "routes": routes
    }