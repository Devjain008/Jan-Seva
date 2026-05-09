from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from pydantic import BaseModel
import hashlib, random, string
from backend.predictive import PredictiveAnalytics
from datetime import datetime, timedelta
from typing import Optional


router = APIRouter(prefix="/admin", tags=["admin"])

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()
def _dept_id(name):
    prefix = "".join(c for c in name.upper() if c.isalpha())[:3]
    return f"{prefix}-{''.join(random.choices(string.digits, k=4))}"

class DeptCreate(BaseModel):
    name: str
    name_hi: str = ""
    category: str
    location: str = ""

class AdminCreate(BaseModel):
    username: str
    password: str


class SLAPolicyCreate(BaseModel):
    category: str
    hours_to_resolve: int
    priority_multiplier: Optional[float] = 1.0

class SLAUpdate(BaseModel):
    hours_to_resolve: Optional[int] = None
    priority_multiplier: Optional[float] = None
    is_active: Optional[bool] = None

# ── setup ─────────────────────────────────────────────────────────────────────
@router.post("/setup")
def setup(data: AdminCreate, db: Session = Depends(get_db)):
    if db.query(models.Admin).filter(models.Admin.username == data.username).first():
        raise HTTPException(400, "Admin already exists")
    db.add(models.Admin(username=data.username, password_hash=_hash(data.password)))
    db.commit()
    return {"success": True}

# ── departments ───────────────────────────────────────────────────────────────
@router.post("/departments")
def create_dept(data: DeptCreate, db: Session = Depends(get_db)):
    did = _dept_id(data.name)
    d = models.Department(name=data.name, name_hi=data.name_hi,
                          dept_id=did, category=data.category, location=data.location)
    db.add(d); db.commit(); db.refresh(d)
    return {"success": True, "dept_id": did, "id": d.id}

@router.get("/departments")
def list_depts(db: Session = Depends(get_db)):
    result = []
    for d in db.query(models.Department).all():
        offs = db.query(models.Official).filter(models.Official.department_id == d.id).all()
        tc = db.query(models.Complaint).filter(models.Complaint.department_id == d.id).count()
        pc = db.query(models.Complaint).filter(models.Complaint.department_id == d.id, models.Complaint.status == "pending").count()
        rc = db.query(models.Complaint).filter(models.Complaint.department_id == d.id, models.Complaint.status.in_(["resolved","closed"])).count()
        result.append({
            "id": d.id, "name": d.name, "name_hi": d.name_hi,
            "dept_id": d.dept_id, "category": d.category, "location": d.location,
            "total_officials": len(offs),
            "approved_officials": sum(1 for o in offs if o.is_approved),
            "total_complaints": tc, "pending_complaints": pc, "resolved_complaints": rc,
        })
    return result

@router.get("/departments/{dept_id}/officials")
def dept_officials(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    offs = db.query(models.Official).filter(models.Official.department_id == dept_id).all()
    return [{
        "id": o.id, "name": o.name, "email": o.email,
        "dept_code": o.dept_code, "is_approved": o.is_approved,
        "department": dept.name if dept else "N/A",
        "total_assigned": o.total_assigned or 0,
        "total_resolved": o.total_resolved or 0,
        "avg_rating": round(o.avg_rating or 0, 2),
        "rating_count": o.rating_count or 0,
        "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""
    } for o in offs]

@router.get("/departments/{dept_id}/complaints")
def dept_complaints(dept_id: int, db: Session = Depends(get_db)):
    rows = db.query(models.Complaint).filter(
        models.Complaint.department_id == dept_id
    ).order_by(models.Complaint.created_at.desc()).all()
    result = []
    for c in rows:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        result.append({
            "id": c.id, "complaint_id": c.complaint_id,
            "category": c.category, "description": c.description,
            "location": c.location or "", "status": c.status, "priority": c.priority,
            "feedback": c.feedback or "",
            "user_name": user.name if user else "Unknown",
            "user_phone": user.phone if user else "",
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p"),
        })
    return result

# ── officials ─────────────────────────────────────────────────────────────────
@router.get("/officials/pending")
def pending(db: Session = Depends(get_db)):
    offs = db.query(models.Official).filter(models.Official.is_approved == False).all()
    result = []
    for o in offs:
        dept = db.query(models.Department).filter(models.Department.id == o.department_id).first()
        result.append({"id": o.id, "name": o.name, "email": o.email,
                        "dept_code": o.dept_code, "department": dept.name if dept else "Unknown",
                        "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""})
    return result

@router.get("/officials/all")
def all_officials(db: Session = Depends(get_db)):
    offs = db.query(models.Official).all()
    result = []
    for o in offs:
        dept = db.query(models.Department).filter(models.Department.id == o.department_id).first()
        result.append({
            "id": o.id, "name": o.name, "email": o.email,
            "dept_code": o.dept_code, "is_approved": o.is_approved,
            "department": dept.name if dept else "Unknown",
            "department_id": o.department_id,
            "total_assigned": o.total_assigned or 0,
            "total_resolved": o.total_resolved or 0,
            "avg_rating": round(o.avg_rating or 0, 2),
            "rating_count": o.rating_count or 0,
            "joined": o.created_at.strftime("%d %b %Y") if o.created_at else ""
        })
    return result

@router.put("/officials/{oid}/approve")
def approve(oid: int, db: Session = Depends(get_db)):
    o = db.query(models.Official).filter(models.Official.id == oid).first()
    if not o: raise HTTPException(404, "Not found")
    o.is_approved = True; db.commit()
    return {"success": True}

@router.put("/officials/{oid}/reject")
def reject(oid: int, db: Session = Depends(get_db)):
    o = db.query(models.Official).filter(models.Official.id == oid).first()
    if not o: raise HTTPException(404, "Not found")
    db.delete(o); db.commit()
    return {"success": True}

# ── official ratings ──────────────────────────────────────────────────────────
@router.get("/officials/{oid}/ratings")
def official_ratings(oid: int, db: Session = Depends(get_db)):
    """Return all ratings given to a specific official, most recent first."""
    ratings = (
        db.query(models.Rating)
        .filter(models.Rating.official_id == oid)
        .order_by(models.Rating.created_at.desc())
        .limit(20)
        .all()
    )
    result = []
    for r in ratings:
        complaint = db.query(models.Complaint).filter(models.Complaint.id == r.complaint_id).first()
        user = db.query(models.User).filter(models.User.id == r.user_id).first()
        result.append({
            "id": r.id,
            "stars": r.stars,
            "comment": r.comment or "",
            "complaint_id": complaint.complaint_id if complaint else "N/A",
            "user_name": user.name if user else "Unknown",
            "created_at": r.created_at.strftime("%d %b %Y, %I:%M %p") if r.created_at else "",
        })
    return result

# ── leaderboard ───────────────────────────────────────────────────────────────
MIN_RESOLVED = 1   # lower threshold for demo (use 5 in production)

@router.get("/leaderboard/overall")
def overall_leaderboard(db: Session = Depends(get_db)):
    offs = db.query(models.Official).filter(models.Official.is_approved == True).all()
    board = []
    for o in offs:
        dept = db.query(models.Department).filter(models.Department.id == o.department_id).first()
        res_rate = round((o.total_resolved or 0) / max(o.total_assigned or 1, 1) * 100, 1)
        res_rate = min(res_rate, 100)   # ✅ Cap at 100%
        board.append({
            "id": o.id, "name": o.name,
            "department": dept.name if dept else "N/A",
            "department_id": o.department_id,
            "total_assigned": o.total_assigned or 0,
            "total_resolved": o.total_resolved or 0,
            "avg_rating": round(o.avg_rating or 0, 2),
            "rating_count": o.rating_count or 0,
            "resolution_rate": res_rate,
            "eligible": (o.total_resolved or 0) >= MIN_RESOLVED,
        })
    eligible   = sorted([b for b in board if b["eligible"]],
                        key=lambda x: (-x["avg_rating"], -x["total_resolved"]))
    ineligible = sorted([b for b in board if not b["eligible"]],
                        key=lambda x: -x["total_resolved"])
    ranked = []
    for i, b in enumerate(eligible + ineligible):
        b["rank"] = i + 1 if b["eligible"] else "-"
        ranked.append(b)
    return ranked

@router.get("/leaderboard/department/{dept_id}")
def dept_leaderboard(dept_id: int, db: Session = Depends(get_db)):
    offs = db.query(models.Official).filter(
        models.Official.department_id == dept_id,
        models.Official.is_approved == True
    ).all()
    board = []
    for o in offs:
        res_rate = round((o.total_resolved or 0) / max(o.total_assigned or 1, 1) * 100, 1)
        res_rate = min(res_rate, 100)   # ✅ Cap at 100%
        board.append({
            "id": o.id, "name": o.name,
            "total_assigned": o.total_assigned or 0,
            "total_resolved": o.total_resolved or 0,
            "avg_rating": round(o.avg_rating or 0, 2),
            "rating_count": o.rating_count or 0,
            "resolution_rate": res_rate,
            "eligible": (o.total_resolved or 0) >= MIN_RESOLVED,
        })
    eligible   = sorted([b for b in board if b["eligible"]],
                        key=lambda x: (-x["avg_rating"], -x["total_resolved"]))
    ineligible = [b for b in board if not b["eligible"]]
    ranked = []
    for i, b in enumerate(eligible):
        b["rank"] = i + 1
        ranked.append(b)
    for b in ineligible:
        b["rank"] = "-"
        ranked.append(b)
    return ranked

# ── stats ─────────────────────────────────────────────────────────────────────
@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(models.Complaint).count()
    resolved = db.query(models.Complaint).filter(
        models.Complaint.status.in_(["resolved","closed"])).count()
    return {
        "total_users":        db.query(models.User).count(),
        "total_complaints":   total,
        "total_departments":  db.query(models.Department).count(),
        "total_officials":    db.query(models.Official).count(),
        "approved_officials": db.query(models.Official).filter(models.Official.is_approved == True).count(),
        "pending_approval":   db.query(models.Official).filter(models.Official.is_approved == False).count(),
        "total_schemes":      db.query(models.Scheme).count(),
        "total_ratings":      db.query(models.Rating).count(),
        "resolved":  resolved,
        "in_progress": db.query(models.Complaint).filter(models.Complaint.status == "in_progress").count(),
        "pending":   db.query(models.Complaint).filter(models.Complaint.status == "pending").count(),
        "rejected":  db.query(models.Complaint).filter(models.Complaint.status == "rejected").count(),
        "resolution_rate": round(resolved / max(total, 1) * 100, 1),
    }

@router.get("/officials/{official_id}/performance")
def get_official_performance(official_id: int, db: Session = Depends(get_db)):
    """Get performance metrics for a specific official"""
    official = db.query(models.Official).filter(models.Official.id == official_id).first()
    if not official:
        raise HTTPException(404, "Official not found")
    
    success_rate = round((official.total_resolved or 0) / max(official.total_assigned or 1, 1) * 100, 1)
    
    # Calculate rank in department
    dept_officials = db.query(models.Official).filter(
        models.Official.department_id == official.department_id,
        models.Official.is_approved == True,
        models.Official.total_resolved >= MIN_RESOLVED
    ).order_by(models.Official.avg_rating.desc()).all()
    
    rank = next((i+1 for i, o in enumerate(dept_officials) if o.id == official_id), None)
    
    return {
        "total_assigned": official.total_assigned or 0,
        "total_resolved": official.total_resolved or 0,
        "avg_rating": round(official.avg_rating or 0, 2),
        "rating_count": official.rating_count or 0,
        "success_rate": success_rate,
        "eligible_for_ranking": (official.total_resolved or 0) >= MIN_RESOLVED,
        "rank_in_department": rank,
        "min_resolved_threshold": MIN_RESOLVED
    }

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """Get overall leaderboard across all departments"""
    return overall_leaderboard(db)

@router.get("/leaderboard/stats")
def leaderboard_stats(db: Session = Depends(get_db)):
    """Get summary stats for leaderboard"""
    officials = db.query(models.Official).filter(models.Official.is_approved == True).all()
    
    total_officials = len(officials)
    eligible = len([o for o in officials if (o.total_resolved or 0) >= MIN_RESOLVED])
    total_resolved = sum(o.total_resolved or 0 for o in officials)
    total_assigned = sum(o.total_assigned or 0 for o in officials)
    
    avg_rating_all = sum(o.avg_rating or 0 for o in officials if o.rating_count > 0) / max(len([o for o in officials if o.rating_count > 0]), 1)
    
    # Department breakdown
    dept_stats = []
    depts = db.query(models.Department).all()
    for dept in depts:
        dept_officials = [o for o in officials if o.department_id == dept.id]
        if dept_officials:
            dept_stats.append({
                "name": dept.name,
                "official_count": len(dept_officials),
                "eligible_count": len([o for o in dept_officials if (o.total_resolved or 0) >= MIN_RESOLVED]),
                "total_resolved": sum(o.total_resolved or 0 for o in dept_officials),
                "avg_rating": sum(o.avg_rating or 0 for o in dept_officials if o.rating_count > 0) / max(len([o for o in dept_officials if o.rating_count > 0]), 1)
            })
    
    return {
        "total_officials": total_officials,
        "eligible_officials": eligible,
        "ineligible_officials": total_officials - eligible,
        "total_resolved": total_resolved,
        "total_assigned": total_assigned,
        "overall_resolution_rate": round(total_resolved / max(total_assigned, 1) * 100, 1),
        "avg_rating_all": round(avg_rating_all, 2),
        "department_breakdown": dept_stats
    }



# ── Predictive Governance Endpoints ──────────────────────────────────────────
@router.get("/predictive/risk-zones")
def get_risk_zones(
    threshold: int = 3, 
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Detect areas at risk of future complaints
    Returns zones with risk levels: critical, high, medium, low
    """
    predictor = PredictiveAnalytics(db)
    risk_zones = predictor.detect_risk_zones(threshold=threshold, days_back=days_back)
    return {
        "success": True,
        "risk_zones": risk_zones,
        "total_zones": len(risk_zones),
        "analysis_period_days": days_back
    }


@router.get("/predictive/workload-forecast")
def get_workload_forecast(
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    """
    Predict department workload for upcoming days
    """
    predictor = PredictiveAnalytics(db)
    forecast = predictor.predict_department_workload(days_ahead=days_ahead)
    return {
        "success": True,
        "forecast": forecast,
        "forecast_days": days_ahead
    }


@router.get("/predictive/hotspots")
def get_hotspots(
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Identify geographic complaint hotspots from geotagged complaints
    """
    predictor = PredictiveAnalytics(db)
    hotspots = predictor.get_hotspots(top_n=top_n)
    return {
        "success": True,
        "hotspots": hotspots
    }


@router.get("/predictive/alert-summary")
def get_alert_summary(db: Session = Depends(get_db)):
    """
    Get comprehensive predictive alert summary for admin dashboard
    """
    predictor = PredictiveAnalytics(db)
    summary = predictor.generate_alert_summary()
    return {
        "success": True,
        "summary": summary
    }


@router.get("/predictive/trends")
def get_complaint_trends(
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get complaint trends analysis over time
    """
    predictor = PredictiveAnalytics(db)
    trends = predictor.get_complaint_trends(days_back=days_back)
    return {
        "success": True,
        "trends": trends
    }

@router.get("/sla/policies")
def get_sla_policies(db: Session = Depends(get_db)):
    """Get all SLA policies"""
    policies = db.query(models.SLAPolicy).all()
    return [
        {
            "id": p.id,
            "category": p.category,
            "hours_to_resolve": p.hours_to_resolve,
            "priority_multiplier": p.priority_multiplier,
            "is_active": p.is_active,
            "created_at": p.created_at.strftime("%d %b %Y") if p.created_at else ""
        }
        for p in policies
    ]

@router.post("/sla/policies")
def create_sla_policy(data: SLAPolicyCreate, db: Session = Depends(get_db)):
    """Create or update SLA policy for a category"""
    existing = db.query(models.SLAPolicy).filter(models.SLAPolicy.category == data.category).first()
    if existing:
        existing.hours_to_resolve = data.hours_to_resolve
        existing.priority_multiplier = data.priority_multiplier
        existing.updated_at = datetime.utcnow()
        db.commit()
        return {"success": True, "message": "SLA policy updated"}
    
    policy = models.SLAPolicy(
        category=data.category,
        hours_to_resolve=data.hours_to_resolve,
        priority_multiplier=data.priority_multiplier
    )
    db.add(policy)
    db.commit()
    return {"success": True, "message": "SLA policy created"}

@router.put("/sla/policies/{policy_id}")
def update_sla_policy(policy_id: int, data: SLAUpdate, db: Session = Depends(get_db)):
    """Update SLA policy"""
    policy = db.query(models.SLAPolicy).filter(models.SLAPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(404, "SLA policy not found")
    
    if data.hours_to_resolve is not None:
        policy.hours_to_resolve = data.hours_to_resolve
    if data.priority_multiplier is not None:
        policy.priority_multiplier = data.priority_multiplier
    if data.is_active is not None:
        policy.is_active = data.is_active
    
    policy.updated_at = datetime.utcnow()
    db.commit()
    return {"success": True}

@router.delete("/sla/policies/{policy_id}")
def delete_sla_policy(policy_id: int, db: Session = Depends(get_db)):
    """Delete SLA policy"""
    policy = db.query(models.SLAPolicy).filter(models.SLAPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(404, "SLA policy not found")
    db.delete(policy)
    db.commit()
    return {"success": True}

@router.get("/sla/overdue-complaints")
def get_overdue_complaints(db: Session = Depends(get_db)):
    """Get all overdue complaints"""
    now = datetime.utcnow()
    overdue = db.query(models.Complaint).filter(
        models.Complaint.status.in_(["pending", "in_progress"]),
        models.Complaint.sla_deadline < now,
        models.Complaint.sla_deadline.isnot(None)
    ).order_by(models.Complaint.sla_deadline.asc()).all()
    
    result = []
    for c in overdue:
        user = db.query(models.User).filter(models.User.id == c.user_id).first()
        dept = db.query(models.Department).filter(models.Department.id == c.department_id).first()
        
        # Calculate overdue duration
        overdue_hours = (now - c.sla_deadline).total_seconds() / 3600
        
        result.append({
            "id": c.id,
            "complaint_id": c.complaint_id,
            "category": c.category,
            "description": c.description[:100],
            "status": c.status,
            "priority": c.priority,
            "location": c.location,
            "user_name": user.name if user else "Unknown",
            "department": dept.name if dept else "Unknown",
            "sla_deadline": c.sla_deadline.strftime("%d %b %Y, %I:%M %p"),
            "overdue_hours": round(overdue_hours, 1),
            "created_at": c.created_at.strftime("%d %b %Y, %I:%M %p")
        })
    
    return {
        "success": True,
        "overdue_count": len(result),
        "complaints": result
    }

@router.get("/sla/compliance-stats")
def get_sla_compliance_stats(db: Session = Depends(get_db)):
    """Get SLA compliance statistics"""
    # Get all resolved complaints with SLA data
    resolved = db.query(models.Complaint).filter(
        models.Complaint.status.in_(["resolved", "closed"]),
        models.Complaint.sla_deadline.isnot(None)
    ).all()
    
    total_resolved = len(resolved)
    met_sla = len([c for c in resolved if not c.SLA_breached])
    breached = total_resolved - met_sla
    
    # Category-wise compliance
    category_stats = {}
    for c in resolved:
        cat = c.category
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "met": 0, "breached": 0}
        category_stats[cat]["total"] += 1
        if c.SLA_breached:
            category_stats[cat]["breached"] += 1
        else:
            category_stats[cat]["met"] += 1
    
    # Calculate compliance percentages
    for cat in category_stats:
        total = category_stats[cat]["total"]
        category_stats[cat]["compliance_rate"] = round(
            category_stats[cat]["met"] / total * 100, 1
        ) if total > 0 else 0
    
    return {
        "success": True,
        "total_resolved": total_resolved,
        "met_sla": met_sla,
        "breached_sla": breached,
        "overall_compliance_rate": round(met_sla / max(total_resolved, 1) * 100, 1),
        "category_stats": category_stats
    }