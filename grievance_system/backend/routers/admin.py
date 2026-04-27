from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
from typing import Optional
import hashlib, random, string
from datetime import datetime
from sqlalchemy import func

router = APIRouter(prefix="/admin", tags=["admin"])

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def generate_dept_id(name: str):
    prefix = ''.join(c for c in name.upper() if c.isalpha())[:3]
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{suffix}"

class DepartmentCreate(BaseModel):
    name: str
    name_hi: str = ""
    category: str
    location: str = ""

class AdminCreate(BaseModel):
    username: str
    password: str

class OfficialAction(BaseModel):
    action: str   # "approve" | "reject"
    reason: str = ""

MIN_RESOLVED_FOR_RANKING = 5

# ── setup ─────────────────────────────────────────────────────────────────────
@router.post("/setup")
def setup_admin(data: AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).filter(models.Admin.username == data.username).first()
    if existing:
        raise HTTPException(400, "Admin already exists")
    db.add(models.Admin(username=data.username, password_hash=hash_password(data.password)))
    db.commit()
    return {"success": True}

# ── departments ───────────────────────────────────────────────────────────────
@router.post("/departments")
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    dept_id = generate_dept_id(data.name)
    dept = models.Department(name=data.name, name_hi=data.name_hi,
                             dept_id=dept_id, category=data.category, location=data.location)
    db.add(dept); db.commit(); db.refresh(dept)
    return {"success": True, "dept_id": dept_id, "id": dept.id}

@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(models.Department).all()
    result = []
    for d in depts:
        officials = db.query(models.Official).filter(models.Official.department_id == d.id).all()
        complaint_count = db.query(models.Complaint).filter(models.Complaint.department_id == d.id).count()
        pending_count   = db.query(models.Complaint).filter(models.Complaint.department_id == d.id,
                                                             models.Complaint.status == "pending").count()
        resolved_count  = db.query(models.Complaint).filter(models.Complaint.department_id == d.id,
                                                             models.Complaint.status == "resolved").count()
        result.append({
            "id": d.id, "name": d.name, "name_hi": d.name_hi,
            "dept_id": d.dept_id, "category": d.category, "location": d.location,
            "total_officials": len(officials),
            "approved_officials": len([o for o in officials if o.is_approved]),
            "total_complaints": complaint_count,
            "pending_complaints": pending_count,
            "resolved_complaints": resolved_count,
        })
    return result

@router.get("/departments/{dept_id}/officials")
def dept_officials(dept_id: int, db: Session = Depends(get_db)):
    officials = db.query(models.Official).filter(models.Official.department_id == dept_id).all()
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    result = []
    for o in officials:
        result.append({
            "id": o.id, "name": o.name, "email": o.email,
            "dept_code": o.dept_code, "is_approved": o.is_approved,
            "department": dept.name if dept else "N/A",
            "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""
        })
    return result

@router.get("/departments/{dept_id}/complaints")
def dept_complaints(dept_id: int, db: Session = Depends(get_db)):
    comps = db.query(models.Complaint).filter(
        models.Complaint.department_id == dept_id
    ).order_by(models.Complaint.created_at.desc()).all()
    result = []
    for c in comps:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        result.append({
            "id": c.id, "complaint_id": c.complaint_id,
            "category": c.category, "description": c.description,
            "location": c.location, "status": c.status, "priority": c.priority,
            "user_name": user.name if user else "Unknown",
            "user_phone": user.phone if user else "",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
        })
    return result

# ── officials ─────────────────────────────────────────────────────────────────
@router.get("/officials/pending")
def pending_officials(db: Session = Depends(get_db)):
    officials = db.query(models.Official).filter(models.Official.is_approved == False).all()
    result = []
    for o in officials:
        dept = db.query(models.Department).filter(models.Department.id == o.department_id).first()
        result.append({
            "id": o.id, "name": o.name, "email": o.email,
            "dept_code": o.dept_code,
            "department": dept.name if dept else "Unknown",
            "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""
        })
    return result

@router.get("/officials/all")
def all_officials(db: Session = Depends(get_db)):
    officials = db.query(models.Official).all()
    result = []
    for o in officials:
        dept = db.query(models.Department).filter(models.Department.id == o.department_id).first()
        result.append({
            "id": o.id, "name": o.name, "email": o.email,
            "dept_code": o.dept_code, "is_approved": o.is_approved,
            "department": dept.name if dept else "Unknown",
            "department_id": o.department_id,
            "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""
        })
    return result

@router.put("/officials/{official_id}/approve")
def approve_official(official_id: int, db: Session = Depends(get_db)):
    o = db.query(models.Official).filter(models.Official.id == official_id).first()
    if not o: raise HTTPException(404, "Not found")
    o.is_approved = True
    db.commit()
    return {"success": True, "action": "approved"}

@router.put("/officials/{official_id}/reject")
def reject_official(official_id: int, db: Session = Depends(get_db)):
    o = db.query(models.Official).filter(models.Official.id == official_id).first()
    if not o: raise HTTPException(404, "Not found")
    db.delete(o); db.commit()
    return {"success": True, "action": "rejected"}

# ── stats ─────────────────────────────────────────────────────────────────────
@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    total = db.query(models.Complaint).count()
    return {
        "total_users":       db.query(models.User).count(),
        "total_complaints":  total,
        "total_departments": db.query(models.Department).count(),
        "total_officials":   db.query(models.Official).count(),
        "approved_officials":db.query(models.Official).filter(models.Official.is_approved == True).count(),
        "pending_approval":  db.query(models.Official).filter(models.Official.is_approved == False).count(),
        "total_schemes":     db.query(models.Scheme).count(),
        "resolved":          db.query(models.Complaint).filter(models.Complaint.status == "resolved").count(),
        "in_progress":       db.query(models.Complaint).filter(models.Complaint.status == "in_progress").count(),
        "pending":           db.query(models.Complaint).filter(models.Complaint.status == "pending").count(),
        "rejected":          db.query(models.Complaint).filter(models.Complaint.status == "rejected").count(),
        "resolution_rate":   round(db.query(models.Complaint).filter(models.Complaint.status == "resolved").count() / max(total,1) * 100, 1),
    }

def _official_perf_row(db: Session, o: models.Official):
    assigned = db.query(models.Complaint).filter(models.Complaint.assigned_official_id == o.id).count()
    resolved = db.query(models.Complaint).filter(
        models.Complaint.assigned_official_id == o.id,
        models.Complaint.status == "resolved"
    ).count()
    avg_rating = db.query(func.avg(models.OfficialRating.rating)).filter(
        models.OfficialRating.official_id == o.id
    ).scalar()
    return {
        "official_id": o.id,
        "name": o.name,
        "department": o.department.name if o.department else "N/A",
        "department_id": o.department_id,
        "total_assigned": assigned,
        "total_resolved": resolved,
        "success_rate": round((resolved / assigned) * 100, 1) if assigned else 0.0,
        "avg_rating": round(float(avg_rating), 2) if avg_rating is not None else 0.0,
    }

def _rank_officials(rows):
    ranked = sorted(rows, key=lambda x: (x["avg_rating"], x["total_resolved"]), reverse=True)
    for i, row in enumerate(ranked, start=1):
        row["rank"] = i
    return ranked

@router.get("/officials/{official_id}/performance")
def official_performance(official_id: int, db: Session = Depends(get_db)):
    official = db.query(models.Official).filter(models.Official.id == official_id).first()
    if not official:
        raise HTTPException(status_code=404, detail="Official not found")

    row = _official_perf_row(db, official)
    dept_rows = [_official_perf_row(db, o) for o in db.query(models.Official).filter(
        models.Official.department_id == official.department_id,
        models.Official.is_approved == True
    ).all()]
    ranked = _rank_officials([r for r in dept_rows if r["total_resolved"] >= MIN_RESOLVED_FOR_RANKING])
    my_rank = next((r["rank"] for r in ranked if r["official_id"] == official_id), None)
    row["rank_in_department"] = my_rank
    row["eligible_for_ranking"] = row["total_resolved"] >= MIN_RESOLVED_FOR_RANKING
    row["min_resolved_threshold"] = MIN_RESOLVED_FOR_RANKING
    return row

@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    approved = db.query(models.Official).filter(models.Official.is_approved == True).all()
    all_rows = [_official_perf_row(db, o) for o in approved]
    eligible_rows = [r for r in all_rows if r["total_resolved"] >= MIN_RESOLVED_FOR_RANKING]

    department_boards = {}
    for dept_id in {r["department_id"] for r in eligible_rows}:
        dept_rows = [r.copy() for r in eligible_rows if r["department_id"] == dept_id]
        if not dept_rows:
            continue
        department_boards[str(dept_id)] = _rank_officials(dept_rows)

    overall = _rank_officials([r.copy() for r in eligible_rows])

    dept_summary = []
    for dept_id in {r["department_id"] for r in all_rows}:
        rows = [r for r in all_rows if r["department_id"] == dept_id]
        if not rows:
            continue
        dept_summary.append({
            "department_id": dept_id,
            "department": rows[0]["department"],
            "officials": len(rows),
            "total_assigned": sum(r["total_assigned"] for r in rows),
            "total_resolved": sum(r["total_resolved"] for r in rows),
            "avg_rating": round(sum(r["avg_rating"] for r in rows) / max(len(rows), 1), 2),
        })
    dept_summary = sorted(dept_summary, key=lambda x: (x["avg_rating"], x["total_resolved"]), reverse=True)

    return {
        "min_resolved_threshold": MIN_RESOLVED_FOR_RANKING,
        "overall": overall,
        "department_wise": department_boards,
        "department_performance": dept_summary,
        "official_metrics": all_rows
    }
