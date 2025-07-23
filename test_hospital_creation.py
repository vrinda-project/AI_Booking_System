#!/usr/bin/env python
import sys
import os
import json

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.hospital import Hospital
from app.models.user import User

def test_hospital_creation():
    db = SessionLocal()
    try:
        # Check if hospital_admin user exists
        hospital_admin = db.query(User).filter(User.role == "hospital_admin").first()
        if hospital_admin:
            print(f"Found hospital_admin user with ID: {hospital_admin.id}")
        else:
            print("No hospital_admin user found")
            return
        
        # Create a test hospital
        hospital = Hospital(
            name="Test Hospital",
            address="123 Test Street",
            phone="+1-555-1234",
            email="test@hospital.com",
            website="https://testhospital.com",
            description="A test hospital",
            status="pending",
            admin_id=hospital_admin.id,
            created_by="test_script"
        )
        
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        
        print(f"Successfully created hospital with ID: {hospital.id}")
        print(json.dumps({
            "id": hospital.id,
            "name": hospital.name,
            "address": hospital.address,
            "phone": hospital.phone,
            "email": hospital.email,
            "admin_id": hospital.admin_id
        }, indent=2))
        
    except Exception as e:
        db.rollback()
        print(f"Error creating hospital: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_hospital_creation()