from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
from typing import Optional
import os, shutil, uuid

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

@router.post("/create")
def create_scheme(data: SchemeCreate, db: Session = Depends(get_db)):
    scheme = models.Scheme(**data.dict())
    db.add(scheme); db.flush()
    _notify_all(db, scheme)
    db.commit(); db.refresh(scheme)
    return {"success": True, "scheme_id": scheme.id}

@router.post("/create-with-image")
async def create_scheme_with_image(
    title: str = Form(...),
    title_hi: str = Form(""),
    description: str = Form(...),
    description_hi: str = Form(""),
    category: str = Form("general"),
    uploaded_by: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_url = ""
    if image and image.filename:
        ext = os.path.splitext(image.filename)[-1].lower()
        if ext not in [".jpg",".jpeg",".png",".webp",".gif"]:
            raise HTTPException(400, "Only jpg/png/webp/gif allowed")
        fname = f"{uuid.uuid4().hex}{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_url = f"http://localhost:8000/uploads/schemes/{fname}"

    scheme = models.Scheme(
        title=title, title_hi=title_hi,
        description=description, description_hi=description_hi,
        category=category, image_url=image_url, uploaded_by=uploaded_by
    )
    db.add(scheme); db.flush()
    _notify_all(db, scheme)
    db.commit(); db.refresh(scheme)
    return {"success": True, "scheme_id": scheme.id, "image_url": image_url}

def _notify_all(db, scheme):
    for user in db.query(models.User).all():
        db.add(models.Notification(
            user_id=user.id, title="New Government Scheme",
            message=f"New scheme available: {scheme.title}",
            notif_type="scheme", ref_id=scheme.id
        ))

@router.get("/all")
def list_schemes(db: Session = Depends(get_db)):
    return [_fmt(s) for s in db.query(models.Scheme).order_by(models.Scheme.created_at.desc()).all()]

@router.get("/{scheme_id}")
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not s: raise HTTPException(404, "Not found")
    return _fmt(s)

@router.delete("/{scheme_id}")
def delete_scheme(scheme_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()
    return {"success": True}

def _fmt(s):
    return {
        "id": s.id, "title": s.title, "title_hi": s.title_hi,
        "description": s.description, "description_hi": s.description_hi,
        "image_url": s.image_url, "category": s.category,
        "created_at": s.created_at.strftime("%d %b %Y"),
    }

@router.get("/user/notifications/{user_id}")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    notifs = db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).limit(30).all()
    return [{
        "id": n.id, "title": n.title, "message": n.message,
        "is_read": n.is_read, "type": n.notif_type,
        "ref_id": n.ref_id, "time": n.created_at.strftime("%d %b, %I:%M %p")
    } for n in notifs]

@router.put("/notifications/{notif_id}/read")
def mark_read(notif_id: int, db: Session = Depends(get_db)):
    n = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if n: n.is_read = True; db.commit()
    return {"success": True}
