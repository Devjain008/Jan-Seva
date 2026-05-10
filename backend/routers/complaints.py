from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import random, string
import math
import shutil
import uuid
import os
from fastapi import File, UploadFile, Form
from backend.models import Official, Complaint as ComplaintModel



router = APIRouter(prefix="/complaints", tags=["complaints"])

# AI Classification Keywords
CAT_KW = {
    "water": ["water", "pipe", "leak", "supply", "पानी", "नल", "पाइप", "jal", "drinking"],
    "electricity": ["electricity", "power", "light", "current", "बिजली", "लाइट", "करंट", "bijli", "voltage"],
    "road": ["road", "pothole", "street", "bridge", "सड़क", "गड्ढा", "पुल", "sadak", "footpath"],
    "waste": ["garbage", "waste", "trash", "dirty", "कचरा", "गंदगी", "सफाई", "kachra", "dump"],
    "drainage": ["drain", "sewer", "flood", "waterlog", "नाला", "सीवर", "जलभराव", "nala", "blockage"],
    "health": ["hospital", "medicine", "health", "doctor", "अस्पताल", "दवा", "स्वास्थ्य", "clinic", "ambulance"],
}

def ai_classify(description, category=None):
    d = description.lower()
    cat = category if (category and category != "other") else None
    if not cat:
        for c, kws in CAT_KW.items():
            if any(kw in d for kw in kws):
                cat = c
                break
    if not cat:
        cat = "other"
    
    priority = "medium"
    urgent_words = ["urgent", "emergency", "danger", "critical", "अत्यावश्यक", "खतरा", "तुरंत", "immediate", "serious"]
    if any(w in d for w in urgent_words):
        priority = "high"
    elif any(w in d for w in ["minor", "small", "slow", "छोटा"]):
        priority = "low"
    return cat, priority

def assign_department(db, category):
    category_map = {
        "water": "water", "electricity": "electricity", "road": "road",
        "waste": "waste", "drainage": "drainage", "health": "health", "other": "other"
    }
    dept_category = category_map.get(category, "other")
    dept = db.query(models.Department).filter(models.Department.category == dept_category).first()
    if not dept:
        dept = db.query(models.Department).filter(models.Department.category == "other").first()
    return dept

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_best_official(db: Session, dept_id: int, lat: Optional[float], lon: Optional[float]) -> Optional[int]:
    """Safe auto-assignment – handles officials without latitude/longitude."""
    officials = db.query(Official).filter(
        Official.department_id == dept_id,
        Official.is_approved == True
    ).all()
    if not officials:
        return None

    if lat is not None and lon is not None:
        nearest = None
        min_dist = float('inf')
        for off in officials:
            # SAFE CHECK – prevents AttributeError
            if hasattr(off, 'latitude') and hasattr(off, 'longitude') and off.latitude and off.longitude:
                dist = haversine(lat, lon, off.latitude, off.longitude)
                if dist < min_dist:
                    min_dist = dist
                    nearest = off.id
        if nearest:
            return nearest

    # Least busy fallback
    busy_counts = {}
    for off in officials:
        count = db.query(ComplaintModel).filter(
            ComplaintModel.official_id == off.id,
            ComplaintModel.status.in_(['pending', 'in_progress'])
        ).count()
        busy_counts[off.id] = count
    if busy_counts:
        least_busy = min(busy_counts, key=busy_counts.get)
        return least_busy

    return officials[0].id

def gen_id():
    return "GR" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Schemas
class ComplaintCreate(BaseModel):
    user_id: int
    category: str
    description: str
    location: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_emergency: bool = False

class StatusUpdate(BaseModel):
    status: str
    note: str = ""
    official_id: Optional[int] = None

class FeedbackIn(BaseModel):
    feedback: str

class RatingIn(BaseModel):
    stars: int
    comment: Optional[str] = None
    user_id: int
    official_id: int

@router.get("/test")
def test():
    return {"message": "Complaints router working"}

UPLOAD_DIR = "uploads/complaints"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/create-with-image")
async def create_complaint_with_image(
    user_id: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location: str = Form(""),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    is_emergency: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Validate user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    
    # Save image if provided
    image_path = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[-1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            raise HTTPException(400, "Only JPG, PNG, WEBP images allowed")
        fname = f"{uuid.uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_path = f"/uploads/complaints/{fname}"

    # AI classification & SLA
    ai_category, priority = ai_classify(description, category)
    if is_emergency:
        priority = "high"
        sla_hours = 4
    else:
        sla_hours = 24 if priority == "high" else 48 if priority == "medium" else 72
    
    department = assign_department(db, ai_category)
    if not department:
        raise HTTPException(500, "No department available")
    
    assigned_official_id = find_best_official(db, department.id, latitude, longitude)
    official_name = None
    if assigned_official_id:
        off = db.query(Official).filter(Official.id == assigned_official_id).first()
        official_name = off.name if off else None
    
    cid = gen_id()
    complaint = models.Complaint(
        complaint_id=cid,
        user_id=user_id,
        department_id=department.id,
        official_id=assigned_official_id,
        category=category,
        ai_category=ai_category,
        description=description,
        location=location or "Unknown",
        latitude=latitude,
        longitude=longitude,
        status="pending",
        is_emergency=is_emergency,
        priority=priority,
        sla_deadline=datetime.utcnow() + timedelta(hours=sla_hours),
        image_path=image_path   # new column
    )
    db.add(complaint)
    db.flush()
    
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status="pending",
        note=f"Complaint filed. AI: {ai_category}, Priority: {priority}." +
             (f" Assigned to {official_name}." if official_name else "")
    )
    db.add(timeline)
    
    notification = models.Notification(
        user_id=user_id,
        title="✅ Complaint Received",
        message=f"Your complaint #{cid} received. Department: {department.name}.",
        notif_type="complaint",
        ref_id=complaint.id
    )
    db.add(notification)
    
    db.commit()
    db.refresh(complaint)
    
    return {
        "success": True,
        "complaint_id": cid,
        "ai_category": ai_category,
        "priority": priority,
        "department": department.name,
        "assigned_official_id": assigned_official_id,
        "assigned_official_name": official_name,
        "status": "pending",
        "image_path": image_path
    }



@router.post("/create")
def create_complaint(data: ComplaintCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, f"User {data.user_id} not found")
    
    ai_category, priority = ai_classify(data.description, data.category)
    if data.is_emergency:
        priority = "high"
        sla_hours = 4
    else:
        sla_hours = 24 if priority == "high" else 48 if priority == "medium" else 72
    
    department = assign_department(db, ai_category)
    if not department:
        raise HTTPException(500, "No department available")
    
    assigned_official_id = find_best_official(db, department.id, data.latitude, data.longitude)
    official_name = None
    if assigned_official_id:
        off = db.query(Official).filter(Official.id == assigned_official_id).first()
        official_name = off.name if off else None
    
    cid = gen_id()
    complaint = models.Complaint(
        complaint_id=cid,
        user_id=data.user_id,
        department_id=department.id,
        official_id=assigned_official_id,
        category=data.category,
        ai_category=ai_category,
        description=data.description,
        location=data.location or "Unknown",
        latitude=data.latitude,
        longitude=data.longitude,
        status="pending",
        is_emergency=data.is_emergency,
        priority=priority,
        sla_deadline=datetime.utcnow() + timedelta(hours=sla_hours)
    )
    db.add(complaint)
    db.flush()
    
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status="pending",
        note=f"Complaint filed. AI: {ai_category}, Priority: {priority}." +
             (f" Assigned to {official_name}." if official_name else "")
    )
    db.add(timeline)
    
    notification = models.Notification(
        user_id=data.user_id,
        title="✅ Complaint Received",
        message=f"Your complaint #{cid} received. Department: {department.name}.",
        notif_type="complaint",
        ref_id=complaint.id
    )
    db.add(notification)
    
    db.commit()
    db.refresh(complaint)
    
    return {
        "success": True,
        "complaint_id": cid,
        "ai_category": ai_category,
        "priority": priority,
        "department": department.name,
        "assigned_official_id": assigned_official_id,
        "assigned_official_name": official_name,
        "status": "pending"
    }

# All other endpoints (user, department, all, stats, etc.) remain unchanged.
# Include them as in your original file – they work fine.
# ── Get User Complaints ──────────────────────────────────────────────────────
@router.get("/user/{user_id}")
def get_user_complaints(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []
    complaints = db.query(models.Complaint).filter(
        models.Complaint.user_id == user_id
    ).order_by(models.Complaint.created_at.desc()).all()
    
    result = []
    for c in complaints:
        dept_name = None
        if c.department_id:
            dept = db.query(models.Department).filter(models.Department.id == c.department_id).first()
            dept_name = dept.name if dept else None
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "ai_category": c.ai_category,
            "description": c.description,
            "location": c.location,
            "status": c.status,
            "priority": c.priority,
            "department": dept_name,
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p") if c.created_at else None,
            "sla_deadline": c.sla_deadline.strftime("%d %b %Y, %I:%M %p") if c.sla_deadline else None,
            "is_overdue": c.is_overdue or False,
        })
    return result

# ── Get Department Complaints (FOR OFFICIALS) ────────────────────────────────
@router.get("/department/{dept_id}")
def get_department_complaints(dept_id: int, status_filter: str = "all", db: Session = Depends(get_db)):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        return []
    query = db.query(models.Complaint).filter(models.Complaint.department_id == dept_id)
    if status_filter == "pending":
        query = query.filter(models.Complaint.status == "pending")
    elif status_filter == "in_progress":
        query = query.filter(models.Complaint.status == "in_progress")
    elif status_filter == "resolved":
        query = query.filter(models.Complaint.status.in_(["resolved", "closed"]))
    elif status_filter == "rejected":
        query = query.filter(models.Complaint.status == "rejected")
    complaints = query.order_by(models.Complaint.created_at.desc()).all()
    
    result = []
    for c in complaints:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "description": c.description,
            "location": c.location or "",
            "status": c.status,
            "priority": c.priority,
            "user_name": user.name if user else "Unknown",
            "user_phone": user.phone if user else "",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p") if c.created_at else "",
            "sla_deadline": c.sla_deadline.strftime("%d %b %Y, %I:%M %p") if c.sla_deadline else None,
            "is_overdue": c.is_overdue or False,
        })
    return result

@router.get("/categories")
def get_complaint_categories(db: Session = Depends(get_db)):
    """Return all distinct department categories for complaint filing."""
    categories = db.query(models.Department.category).distinct().all()
    cat_list = [c[0] for c in categories if c[0]]
    if "other" not in cat_list:
        cat_list.append("other")
    return {"categories": cat_list}

# ── Get All Complaints (Admin) ───────────────────────────────────────────────
@router.get("/all")
def get_all_complaints(db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()
    result = []
    for c in complaints:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        dept = db.query(models.Department).filter(models.Department.id == c.department_id).first()
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "description": c.description[:150],
            "location": c.location,
            "status": c.status,
            "priority": c.priority,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "is_emergency": c.is_emergency or False,
            "user_name": user.name if user else "Unknown",
            "user_phone": user.phone if user else "",
            "department": dept.name if dept else "Unassigned",
            "image_path": c.image_path,
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p") if c.created_at else None,
            "sla_deadline": c.sla_deadline.strftime("%d %b %Y, %I:%M %p") if c.sla_deadline else None,
            "is_overdue": c.is_overdue or False,
        })
    return result

# ── Update Complaint Status ───────────────────────────────────────────────────
@router.put("/{complaint_id}/status")
def update_status(complaint_id: str, data: StatusUpdate, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    
    old_status = complaint.status
    complaint.status = data.status
    complaint.updated_at = datetime.utcnow()
    
    if data.status == "resolved":
        complaint.resolved_at = datetime.utcnow()
        complaint.feedback_deadline = datetime.utcnow() + timedelta(days=2)
        if data.official_id:
            complaint.official_id = data.official_id
            official = db.query(models.Official).filter(models.Official.id == data.official_id).first()
            if official:
                official.total_resolved = (official.total_resolved or 0) + 1
    
    if old_status == "pending" and data.status == "in_progress" and data.official_id:
        official = db.query(models.Official).filter(models.Official.id == data.official_id).first()
        if official:
            official.total_assigned = (official.total_assigned or 0) + 1
    
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status=data.status,
        note=data.note or f"Status updated to {data.status}"
    )
    db.add(timeline)
    
    notification = models.Notification(
        user_id=complaint.user_id,
        title="Complaint Status Update",
        message=f"Your complaint #{complaint_id} status: {data.status}",
        notif_type="complaint",
        ref_id=complaint.id
    )
    db.add(notification)
    db.commit()
    
    return {"success": True, "status": data.status}

# ── Submit Feedback ──────────────────────────────────────────────────────────
@router.put("/{complaint_id}/feedback")
def submit_feedback(complaint_id: str, data: FeedbackIn, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    complaint.feedback = data.feedback
    if data.feedback == "satisfied":
        complaint.status = "closed"
        note = "User confirmed satisfied. Case closed."
    else:
        complaint.status = "in_progress"
        complaint.feedback_deadline = None
        note = "User not satisfied. Complaint reopened."
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status=complaint.status,
        note=note
    )
    db.add(timeline)
    db.commit()
    return {"success": True, "new_status": complaint.status}

# ── Rate Complaint ───────────────────────────────────────────────────────────
@router.post("/{complaint_id}/rate")
def rate_complaint(complaint_id: str, data: RatingIn, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    if complaint.rating:
        raise HTTPException(400, "Already rated")
    rating = models.Rating(
        complaint_id=complaint.id,
        user_id=data.user_id,
        official_id=data.official_id,
        stars=data.stars,
        comment=data.comment
    )
    db.add(rating)
    db.flush()
    official = db.query(models.Official).filter(models.Official.id == data.official_id).first()
    if official:
        old_sum = (official.avg_rating or 0) * (official.rating_count or 0)
        official.rating_count = (official.rating_count or 0) + 1
        official.avg_rating = round((old_sum + data.stars) / official.rating_count, 2)
    db.commit()
    return {"success": True, "avg_rating": official.avg_rating if official else data.stars}

# ── Get Stats ────────────────────────────────────────────────────────────────
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Complaint).count()
    return {
        "total": total,
        "pending": db.query(models.Complaint).filter(models.Complaint.status == "pending").count(),
        "in_progress": db.query(models.Complaint).filter(models.Complaint.status == "in_progress").count(),
        "resolved": db.query(models.Complaint).filter(models.Complaint.status == "resolved").count(),
        "closed": db.query(models.Complaint).filter(models.Complaint.status == "closed").count(),
        "rejected": db.query(models.Complaint).filter(models.Complaint.status == "rejected").count(),
    }