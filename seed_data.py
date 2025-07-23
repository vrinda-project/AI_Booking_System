#!/usr/bin/env python
import sys
import os
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def seed_users(db: Session):
    """Seed demo users into the database"""
    
    # Demo user data
    users_data = [
        {
            "email": "admin@hospital.com",
            "password": "password123",
            "full_name": "Super Admin",
            "role": "super_admin",
            "phone": "+1234567890"
        },
        {
            "email": "hospital@admin.com",
            "password": "password123",
            "full_name": "Hospital Admin",
            "role": "hospital_admin",
            "phone": "+1234567891"
        },
        {
            "email": "doctor@hospital.com",
            "password": "password123",
            "full_name": "Dr. Smith",
            "role": "doctor",
            "phone": "+1234567892"
        },
        {
            "email": "agent@hospital.com",
            "password": "password123",
            "full_name": "Booking Agent",
            "role": "agent",
            "phone": "+1234567893"
        },
        {
            "email": "patient@hospital.com",
            "password": "password123",
            "full_name": "John Patient",
            "role": "patient",
            "phone": "+1234567894"
        }
    ]
    
    # Create users
    for i, user_data in enumerate(users_data):
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"User with email {user_data['email']} already exists. Skipping.")
            continue
        
        # Create new user
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone=user_data["phone"],
            is_active=True,
            email_verified=False,
            phone_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="seed_script",
            updated_by="seed_script"
        )
        
        db.add(user)
        print(f"Added user: {user_data['email']} with role {user_data['role']}")
    
    # Commit the changes
    db.commit()
    print("User seeding completed successfully!")


def main():
    """Main function to seed the database"""
    print("Starting database seeding...")
    
    # Create a database session
    db = SessionLocal()
    try:
        # Seed users
        seed_users(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()
    
    print("Database seeding completed!")


if __name__ == "__main__":
    main()