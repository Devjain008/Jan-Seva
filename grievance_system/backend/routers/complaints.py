from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
from datetime import datetime
import random, string, re
from typing import Optional

router = APIRouter(prefix="/complaints", tags=["complaints"])

CATEGORY_KEYWORDS = {
    "water": ["water", "pipe", "leak", "supply", "पानी", "नल", "पाइप"],
    "electricity": ["electricity", "power", "light", "current", "बिजली", "लाइट", "करंट"],
    "road": ["road", "pothole", "street", "bridge", "सड़क", "गड्ढा", "पुल"],
    "waste": ["garbage", "waste", "trash", "dirty", "कचरा", "गंदगी", "सफाई"],
    "drainage": ["drain", "sewer", "flood", "waterlog", "नाला", "सीवर", "जलभराव"],
    "health": ["hospital", "medicine", "health", "doctor", "अस्पताल", "दवा", "स्वास्थ्य"],
}

PRIORITY_KEYWORDS = {
    "high": ["urgent", "emergency", "danger", "critical", "अत्यावश्यक", "खतरा", "तुरंत"],
    "low": ["minor", "small", "slow", "छोटा", "साधारण"],
}

def ai_classify(description: str, category: str = None):
    desc_lower = description.lower()
    detected_cat = category
    if not detected_cat or detected_cat == "other":
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in desc_lower for kw in keywords):
                detected_cat = cat
                break
    if not detected_cat:
        detected_cat = "other"
    priority = "medium"
    for p, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            priority = p
            break
    return detected_cat, priority

def generate_complaint_id():
    chars = string.ascii_uppercase + string.digits
    return "GR" + ''.join(random.choices(chars, k=8))

def assign_department(db: Session, category: str, location: str = None):
    dept = db.query(models.Department).filter(models.Department.category == category).first()
    if not dept:
        dept = db.query(models.Department).first()
    return dept

class ComplaintCreate(BaseModel):
    user_id: int
    category: str
    description: str
    location: str = ""
    latitude: float = None
    longitude: float = None

class ComplaintFeedback(BaseModel):
    feedback: str  # resolved / not_resolved

class ComplaintStatusUpdate(BaseModel):
    status: str
    note: str = ""
    official_id: Optional[int] = None

class ComplaintRating(BaseModel):
    user_id: int
    rating: int
    comment: str = ""

@router.post("/create")
def create_complaint(data: ComplaintCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ai_cat, priority = ai_classify(data.description, data.category)
    dept = assign_department(db, ai_cat, data.location)
    complaint_id = generate_complaint_id()
    complaint = models.Complaint(
        complaint_id=complaint_id,
        user_id=data.user_id,
        department_id=dept.id if dept else None,
        category=data.category,
        ai_category=ai_cat,
        description=data.description,
        location=data.location,
        latitude=data.latitude,
        longitude=data.longitude,
        status="pending",
        priority=priority,
    )
    db.add(complaint)
    db.flush()
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status="pending",
        note="Complaint filed and under review."
    )
    db.add(timeline)
    notif = models.Notification(
        user_id=data.user_id,
        title="Complaint Filed",
        message=f"Your complaint {complaint_id} has been filed successfully.",
        notif_type="complaint",
        ref_id=complaint.id
    )
    db.add(notif)
    db.commit()
    db.refresh(complaint)
    return {
        "success": True,
        "complaint_id": complaint_id,
        "ai_category": ai_cat,
        "priority": priority,
        "department": dept.name if dept else "General",
        "status": "pending"
    }

@router.get("/user/{user_id}")
def get_user_complaints(user_id: int, db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).filter(models.Complaint.user_id == user_id).order_by(models.Complaint.created_at.desc()).all()
    result = []
    for c in complaints:
        dept = db.query(models.Department).filter(models.Department.id == c.department_id).first()
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "ai_category": c.ai_category,
            "description": c.description[:100] + "..." if len(c.description) > 100 else c.description,
            "location": c.location,
            "status": c.status,
            "priority": c.priority,
            "department": dept.name if dept else "N/A",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
            "feedback": c.feedback,
            "rating": c.rating.rating if c.rating else None
        })
    return result

@router.get("/track/{complaint_id}")
def track_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    dept = db.query(models.Department).filter(models.Department.id == complaint.department_id).first()
    timeline = db.query(models.ComplaintTimeline).filter(
        models.ComplaintTimeline.complaint_id == complaint.id
    ).order_by(models.ComplaintTimeline.created_at.asc()).all()
    return {
        "complaint_id": complaint.complaint_id,
        "category": complaint.category,
        "description": complaint.description,
        "location": complaint.location,
        "status": complaint.status,
        "priority": complaint.priority,
        "department": dept.name if dept else "N/A",
        "created_at": complaint.created_at.strftime("%d %b %Y, %I:%M %p"),
        "updated_at": complaint.updated_at.strftime("%d %b %Y, %I:%M %p"),
        "feedback": complaint.feedback,
        "rating": complaint.rating.rating if complaint.rating else None,
        "rating_comment": complaint.rating.comment if complaint.rating else "",
        "assigned_official_id": complaint.assigned_official_id,
        "timeline": [{"status": t.status, "note": t.note, "time": t.created_at.strftime("%d %b %Y, %I:%M %p")} for t in timeline]
    }

@router.get("/department/{dept_id}")
def get_dept_complaints(dept_id: int, db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).filter(models.Complaint.department_id == dept_id).order_by(models.Complaint.created_at.desc()).all()
    result = []
    for c in complaints:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "description": c.description[:150] + "..." if len(c.description) > 150 else c.description,
            "location": c.location,
            "status": c.status,
            "priority": c.priority,
            "user_name": user.name if user else "Unknown",
            "user_phone": user.phone if user else "",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
        })
    return result

@router.put("/{complaint_id}/status")
def update_status(complaint_id: str, data: ComplaintStatusUpdate, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if data.official_id:
        official = db.query(models.Official).filter(models.Official.id == data.official_id).first()
        if not official:
            raise HTTPException(status_code=404, detail="Official not found")
        complaint.assigned_official_id = data.official_id

    complaint.status = data.status
    complaint.updated_at = datetime.utcnow()
    if data.status == "resolved":
        complaint.resolved_at = datetime.utcnow()
    timeline = models.ComplaintTimeline(
        complaint_id=complaint.id,
        status=data.status,
        note=data.note or f"Status updated to {data.status}"
    )
    db.add(timeline)
    notif = models.Notification(
        user_id=complaint.user_id,
        title="Complaint Update",
        message=(
            f"Your complaint {complaint.complaint_id} is now resolved. "
            "Please rate the official and share feedback."
            if data.status == "resolved"
            else f"Your complaint {complaint.complaint_id} is now {data.status.replace('_',' ').title()}."
        ),
        notif_type="complaint",
        ref_id=complaint.id
    )
    db.add(notif)
    db.commit()
    return {"success": True, "status": data.status}

@router.put("/{complaint_id}/feedback")
def submit_feedback(complaint_id: str, data: ComplaintFeedback, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.feedback = data.feedback
    db.commit()
    return {"success": True}

@router.put("/{complaint_id}/rating")
def submit_rating(complaint_id: str, data: ComplaintRating, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.user_id != data.user_id:
        raise HTTPException(status_code=403, detail="Only complaint owner can rate")
    if complaint.status != "resolved":
        raise HTTPException(status_code=400, detail="Rating is allowed only after resolution")
    if not complaint.assigned_official_id:
        raise HTTPException(status_code=400, detail="No official mapped to this complaint")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    existing = db.query(models.OfficialRating).filter(
        models.OfficialRating.complaint_id == complaint.id
    ).first()
    if existing:
        existing.rating = data.rating
        existing.comment = data.comment
    else:
        db.add(models.OfficialRating(
            complaint_id=complaint.id,
            user_id=data.user_id,
            official_id=complaint.assigned_official_id,
            rating=data.rating,
            comment=data.comment
        ))
    db.commit()
    return {"success": True}

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
            "description": c.description[:100] + "..." if len(c.description) > 100 else c.description,
            "location": c.location,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "status": c.status,
            "priority": c.priority,
            "department": dept.name if dept else "N/A",
            "user_name": user.name if user else "Unknown",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
        })
    return result

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(models.Complaint).count()
    pending = db.query(models.Complaint).filter(models.Complaint.status == "pending").count()
    in_progress = db.query(models.Complaint).filter(models.Complaint.status == "in_progress").count()
    resolved = db.query(models.Complaint).filter(models.Complaint.status == "resolved").count()
    return {"total": total, "pending": pending, "in_progress": in_progress, "resolved": resolved}
