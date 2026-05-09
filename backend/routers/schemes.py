from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
from typing import Optional
import os, shutil, uuid
from datetime import datetime

router = APIRouter(prefix="/schemes", tags=["schemes"])

UPLOAD_DIR = "uploads/schemes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class SchemeCreate(BaseModel):
    title: str
    title_hi: str = ""
    description: str
    description_hi: str = ""
    image_url: str = ""
    category: str = "general"
    uploaded_by: Optional[int] = None
    uploaded_by_type: Optional[str] = None  # "admin" or "official"

@router.post("/create")
def create_scheme(data: SchemeCreate, db: Session = Depends(get_db)):
    """Create scheme and notify all users"""
    scheme = models.Scheme(
        title=data.title,
        title_hi=data.title_hi,
        description=data.description,
        description_hi=data.description_hi,
        image_url=data.image_url,
        category=data.category,
        uploaded_by=data.uploaded_by,
        created_at=datetime.utcnow()
    )
    db.add(scheme)
    db.flush()
    
    # Get uploader info
    uploader_name = "Admin"
    if data.uploaded_by and data.uploaded_by_type == "official":
        official = db.query(models.Official).filter(models.Official.id == data.uploaded_by).first()
        if official:
            uploader_name = official.name
    
    # Notify all users
    users = db.query(models.User).all()
    for user in users:
        notification = models.Notification(
            user_id=user.id,
            title=f"📜 New Scheme: {data.title}",
            message=f"A new government scheme '{data.title}' has been added by {uploader_name}. Check it out!",
            notif_type="scheme",
            ref_id=scheme.id,
            created_at=datetime.utcnow()
        )
        db.add(notification)
    
    db.commit()
    db.refresh(scheme)
    
    return {
        "success": True,
        "scheme_id": scheme.id,
        "message": f"Scheme created and {len(users)} users notified"
    }

@router.post("/create-with-image")
async def create_scheme_with_image(
    title: str = Form(...),
    title_hi: str = Form(""),
    description: str = Form(...),
    description_hi: str = Form(""),
    category: str = Form("general"),
    uploaded_by: Optional[int] = Form(None),
    uploaded_by_type: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create scheme with image upload and notify all users"""
    image_url = ""
    if image and image.filename:
        ext = os.path.splitext(image.filename)[-1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            raise HTTPException(400, "Only jpg/png/webp/gif allowed")
        fname = f"{uuid.uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_url = f"/uploads/schemes/{fname}"
    
    scheme = models.Scheme(
        title=title,
        title_hi=title_hi,
        description=description,
        description_hi=description_hi,
        category=category,
        image_url=image_url,
        uploaded_by=uploaded_by,
        created_at=datetime.utcnow()
    )
    db.add(scheme)
    db.flush()
    
    # Get uploader info
    uploader_name = "Admin"
    if uploaded_by and uploaded_by_type == "official":
        official = db.query(models.Official).filter(models.Official.id == uploaded_by).first()
        if official:
            uploader_name = official.name
    
    # Notify all users
    users = db.query(models.User).all()
    for user in users:
        notification = models.Notification(
            user_id=user.id,
            title=f"📜 New Scheme: {title}",
            message=f"A new government scheme '{title}' has been added by {uploader_name}. Tap to view details!",
            notif_type="scheme",
            ref_id=scheme.id,
            created_at=datetime.utcnow()
        )
        db.add(notification)
    
    db.commit()
    db.refresh(scheme)
    
    # Create voice announcement text
    voice_announcement = f"Attention citizens. A new government scheme has been launched. {title}. {description[:200]}"
    
    return {
        "success": True,
        "scheme_id": scheme.id,
        "image_url": image_url,
        "voice_announcement": voice_announcement,
        "message": f"Scheme created and {len(users)} users notified"
    }

@router.get("/all")
def list_schemes(db: Session = Depends(get_db)):
    """Get all schemes"""
    schemes = db.query(models.Scheme).order_by(models.Scheme.created_at.desc()).all()
    result = []
    for s in schemes:
        # Get uploader name
        uploader_name = "System"
        if s.uploaded_by:
            official = db.query(models.Official).filter(models.Official.id == s.uploaded_by).first()
            if official:
                uploader_name = official.name
            else:
                uploader_name = "Admin"
        
        result.append({
            "id": s.id,
            "title": s.title,
            "title_hi": s.title_hi,
            "description": s.description,
            "description_hi": s.description_hi,
            "image_url": s.image_url,
            "category": s.category,
            "created_at": s.created_at.strftime("%d %b %Y"),
            "uploaded_by": uploader_name,
            "full_created_at": s.created_at.isoformat()
        })
    return result

@router.get("/{scheme_id}")
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Get single scheme details"""
    s = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not s:
        raise HTTPException(404, "Scheme not found")
    
    return {
        "id": s.id,
        "title": s.title,
        "title_hi": s.title_hi,
        "description": s.description,
        "description_hi": s.description_hi,
        "image_url": s.image_url,
        "category": s.category,
        "created_at": s.created_at.strftime("%d %b %Y"),
        "full_description": s.description,
        "full_description_hi": s.description_hi
    }

@router.delete("/{scheme_id}")
def delete_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Delete scheme"""
    s = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not s:
        raise HTTPException(404, "Scheme not found")
    
    # Delete image file if exists
    if s.image_url and s.image_url.startswith("/uploads/"):
        image_path = os.path.join(".", s.image_url.lstrip("/"))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.delete(s)
    db.commit()
    return {"success": True, "message": "Scheme deleted successfully"}


@router.put("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """Mark a single notification as read"""
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    db.commit()
    return {"success": True}

@router.get("/user/notifications/{user_id}")
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    """Get all notifications for a user"""
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).all()
    return [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "notif_type": n.notif_type,
        "ref_id": n.ref_id,
        "time": n.created_at.strftime("%d %b %Y, %I:%M %p") if n.created_at else ""
    } for n in notifs]

@router.put("/notifications/mark-all-read/{user_id}")
def mark_all_notifications_read(user_id: int, db: Session = Depends(get_db)):
    """Mark all notifications for a user as read"""
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"success": True}

@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """Delete a single notification"""
    notif = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    db.delete(notif)
    db.commit()
    return {"success": True}

@router.delete("/notifications/clear-all/{user_id}")
def clear_all_notifications(user_id: int, db: Session = Depends(get_db)):
    """Delete all notifications for a user"""
    db.query(models.Notification).filter(models.Notification.user_id == user_id).delete()
    db.commit()
    return {"success": True}