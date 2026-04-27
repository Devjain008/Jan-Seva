from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database import engine, Base, SessionLocal
from backend import models
from backend.routers import auth, complaints, admin, schemes
import hashlib, os
from sqlalchemy import text
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="AI Citizen Grievance System", version="2.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

os.makedirs("uploads/schemes", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(admin.router)
app.include_router(schemes.router)

def seed_data():
    db = SessionLocal()
    try:
        if not db.query(models.Admin).first():
            db.add(models.Admin(username="admin",
                                password_hash=hashlib.sha256("admin123".encode()).hexdigest()))
            db.commit()

        if not db.query(models.Department).first():
            for d in [
                {"name":"Water Supply Department","name_hi":"जल आपूर्ति विभाग","dept_id":"WAT-0001","category":"water","location":"Bhopal"},
                {"name":"Electricity Department","name_hi":"विद्युत विभाग","dept_id":"ELE-0002","category":"electricity","location":"Bhopal"},
                {"name":"Public Works Department","name_hi":"लोक निर्माण विभाग","dept_id":"PWD-0003","category":"road","location":"Bhopal"},
                {"name":"Municipal Corporation","name_hi":"नगर निगम","dept_id":"MUN-0004","category":"waste","location":"Bhopal"},
                {"name":"Drainage Department","name_hi":"जल निकासी विभाग","dept_id":"DRN-0005","category":"drainage","location":"Bhopal"},
                {"name":"Health Department","name_hi":"स्वास्थ्य विभाग","dept_id":"HLT-0006","category":"health","location":"Bhopal"},
                {"name":"General Administration","name_hi":"सामान्य प्रशासन","dept_id":"GEN-0007","category":"other","location":"Bhopal"},
            ]:
                db.add(models.Department(**d))
            db.commit()

        if not db.query(models.Scheme).first():
            for s in [
                {"title":"PM Awas Yojana","title_hi":"प्रधानमंत्री आवास योजना",
                 "description":"Housing for all: financial assistance to build homes for eligible beneficiaries.",
                 "description_hi":"सभी के लिए आवास: पात्र लाभार्थियों को घर बनाने के लिए वित्तीय सहायता।",
                 "category":"housing","image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png"},
                {"title":"Jal Jeevan Mission","title_hi":"जल जीवन मिशन",
                 "description":"Safe tap water to every rural household by 2024.",
                 "description_hi":"2024 तक हर ग्रामीण घर में नल से शुद्ध पेयजल।",
                 "category":"water","image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png"},
                {"title":"Ujjwala Yojana","title_hi":"उज्ज्वला योजना",
                 "description":"Free LPG connections to BPL women to eliminate indoor pollution.",
                 "description_hi":"BPL महिलाओं को मुफ्त LPG कनेक्शन।",
                 "category":"energy","image_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Emblem_of_India.svg/120px-Emblem_of_India.svg.png"},
            ]:
                db.add(models.Scheme(**s))
            db.commit()
    finally:
        db.close()

def run_migrations():
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(complaints)")).fetchall()
        col_names = {c[1] for c in cols}
        if "assigned_official_id" not in col_names:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN assigned_official_id INTEGER"))

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    run_migrations()
    seed_data()

@app.get("/")
def root(): return {"message": "AI Citizen Grievance System API v2", "status": "running"}

@app.get("/health")
def health(): return {"status": "healthy"}
