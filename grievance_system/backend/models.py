from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime
import enum

class ComplaintStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

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
    created_at = Column(DateTime, default=datetime.utcnow)
    department = relationship("Department", back_populates="officials")
    assigned_complaints = relationship("Complaint", back_populates="assigned_official")
    ratings = relationship("OfficialRating", back_populates="official")

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    assigned_official_id = Column(Integer, ForeignKey("officials.id"), nullable=True)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(200))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="pending")
    priority = Column(String(10), default="medium")
    ai_category = Column(String(50))
    image_url = Column(String(500), nullable=True)
    feedback = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")
    assigned_official = relationship("Official", back_populates="assigned_complaints")
    timeline = relationship("ComplaintTimeline", back_populates="complaint")
    rating = relationship("OfficialRating", back_populates="complaint", uselist=False)

class ComplaintTimeline(Base):
    __tablename__ = "complaint_timeline"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    status = Column(String(50))
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    complaint = relationship("Complaint", back_populates="timeline")

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

class OfficialRating(Base):
    __tablename__ = "official_ratings"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    official_id = Column(Integer, ForeignKey("officials.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    complaint = relationship("Complaint", back_populates="rating")
    official = relationship("Official", back_populates="ratings")
