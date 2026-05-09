# init_db.py - Run this first
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database import engine, Base
from backend import models

def init_database():
    print("Creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database created successfully!")

if __name__ == "__main__":
    init_database()