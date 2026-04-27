from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random, hashlib, string

router = APIRouter(prefix="/auth", tags=["auth"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_complaint_id():
    chars = string.ascii_uppercase + string.digits
    return "GR" + ''.join(random.choices(chars, k=8))

# ---- User Auth ----
class UserSignup(BaseModel):
    name: str
    phone: str
    address: str
    language: str = "en"

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

@router.post("/user/signup")
def user_signup(data: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = models.User(name=data.name, phone=data.phone, address=data.address, language=data.language)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "User registered", "user_id": user.id}

@router.post("/user/send-otp")
def send_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == data.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="Phone not registered")
    otp = generate_otp()
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    # Simulate OTP (in production, send via SMS)
    return {"success": True, "otp": otp, "message": f"OTP sent to {data.phone} (simulated)"}

@router.post("/user/verify-otp")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.phone == data.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    user.otp = None
    db.commit()
    return {"success": True, "user_id": user.id, "name": user.name, "phone": user.phone, "language": user.language, "address": user.address}

# ---- Official Auth ----
class OfficialSignup(BaseModel):
    name: str
    email: str
    password: str
    dept_code: str

class OfficialLogin(BaseModel):
    email: str
    password: str

@router.post("/official/signup")
def official_signup(data: OfficialSignup, db: Session = Depends(get_db)):
    existing = db.query(models.Official).filter(models.Official.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    dept = db.query(models.Department).filter(models.Department.dept_id == data.dept_code).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Invalid Department Code")
    official = models.Official(
        name=data.name, email=data.email,
        password_hash=hash_password(data.password),
        department_id=dept.id, dept_code=data.dept_code,
        is_approved=False
    )
    db.add(official)
    db.commit()
    db.refresh(official)
    return {"success": True, "message": "Registration submitted. Awaiting admin approval."}

@router.post("/official/login")
def official_login(data: OfficialLogin, db: Session = Depends(get_db)):
    official = db.query(models.Official).filter(models.Official.email == data.email).first()
    if not official or official.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not official.is_approved:
        raise HTTPException(status_code=403, detail="Account pending approval")
    dept = db.query(models.Department).filter(models.Department.id == official.department_id).first()
    return {"success": True, "official_id": official.id, "name": official.name, "email": official.email,
            "department": dept.name if dept else "N/A", "department_id": official.department_id}

# ---- Admin Auth ----
class AdminLogin(BaseModel):
    username: str
    password: str

@router.post("/admin/login")
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == data.username).first()
    if not admin or admin.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"success": True, "admin_id": admin.id, "username": admin.username}
