# backend/fix_officials.py - Run this to fix existing officials
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import Official, Department

def fix_officials():
    db = SessionLocal()
    try:
        # Get all officials without department_id
        officials = db.query(Official).filter(
            (Official.department_id == None) | (Official.department_id == 0)
        ).all()
        
        if officials:
            print(f"Found {len(officials)} officials without department")
            
            # Get first department
            dept = db.query(Department).first()
            if dept:
                for official in officials:
                    official.department_id = dept.id
                    print(f"✅ Updated official {official.email} with department_id {dept.id}")
                db.commit()
                print("All officials fixed!")
            else:
                print("No departments found. Please run the app first to create departments.")
        else:
            print("All officials have valid department IDs")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_officials()