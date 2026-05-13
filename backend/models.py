from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    address = Column(Text)
    language = Column(String(10), default="en")
    otp = Column(String(6))
    otp_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    complaints = relationship("Complaint", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    name_hi = Column(String(100))
    dept_id = Column(String(20), unique=True, nullable=False)
    category = Column(String(50))
    location = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    officials = relationship("Official", back_populates="department")
    complaints = relationship("Complaint", back_populates="department")

class Official(Base):
    __tablename__ = "officials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    dept_code = Column(String(20))
    is_approved = Column(Boolean, default=False)
    total_assigned = Column(Integer, default=0)
    total_resolved = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    department = relationship("Department", back_populates="officials")
    ratings = relationship("Rating", back_populates="official")
    complaints = relationship("Complaint", back_populates="official")   # ADDED

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    official_id = Column(Integer, ForeignKey("officials.id"), nullable=True)
    category = Column(String(50), nullable=False)
    ai_category = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="pending")
    is_emergency = Column(Boolean, default=False)          # CRITICAL – was missing
    priority = Column(String(10), default="medium")
    sla_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    feedback_deadline = Column(DateTime, nullable=True)
    feedback = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    is_overdue = Column(Boolean, default=False)
    image_path = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    official = relationship("Official", back_populates="complaints")
    timeline = relationship("ComplaintTimeline", back_populates="complaint")
    rating_obj = relationship("Rating", back_populates="complaint", uselist=False)

class ComplaintTimeline(Base):
    __tablename__ = "complaint_timeline"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    status = Column(String(50))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    complaint = relationship("Complaint", back_populates="timeline")

class Rating(Base):
    __tablename__ = "ratings"
    id           = Column(Integer, primary_key=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    official_id  = Column(Integer, ForeignKey("officials.id"), nullable=True)  # ← nullable=True
    stars        = Column(Integer, nullable=False)
    comment      = Column(String, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    title_hi = Column(String(200))
    description = Column(Text, nullable=False)
    description_hi = Column(Text)
    image_url = Column(String(500))
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(Integer, ForeignKey("officials.id"), nullable=True)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    notif_type = Column(String(50), default="complaint")
    ref_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SLAPolicy(Base):
    __tablename__ = "sla_policies"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, nullable=False)
    hours_to_resolve = Column(Integer, nullable=False)
    priority_multiplier = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)