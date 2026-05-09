# check_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import SessionLocal
from backend import models

def check_database():
    db = SessionLocal()
    try:
        print("=" * 50)
        print("DATABASE DEBUG INFO")
        print("=" * 50)
        
        # Check users
        users = db.query(models.User).all()
        print(f"\n👤 USERS ({len(users)}):")
        for user in users:
            print(f"  - ID: {user.id}, Name: {user.name}, Phone: {user.phone}")
        
        # Check complaints
        complaints = db.query(models.Complaint).all()
        print(f"\n📋 COMPLAINTS ({len(complaints)}):")
        for c in complaints:
            print(f"  - ID: {c.id}, Complaint ID: {c.complaint_id}, User ID: {c.user_id}, Status: {c.status}")
            print(f"    Description: {c.description[:50]}...")
            print(f"    Created: {c.created_at}")
        
        # Check if complaints are linked to users
        print(f"\n🔗 COMPLAINT-USER MAPPING:")
        for user in users:
            user_complaints = db.query(models.Complaint).filter(models.Complaint.user_id == user.id).all()
            print(f"  User {user.name} (ID: {user.id}) has {len(user_complaints)} complaints")
            for c in user_complaints:
                print(f"    - {c.complaint_id}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_database()