"""
Script to run the hospital migration
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.database import Base, engine

def run_migration():
    print("Running hospital migration...")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Add hospital_id column to departments if it doesn't exist
    with engine.connect() as conn:
        try:
            # Check if hospital_id column exists in departments
            conn.execute(text("SELECT hospital_id FROM departments LIMIT 1"))
            print("hospital_id column already exists in departments table")
        except Exception:
            print("Adding hospital_id column to departments table...")
            conn.execute(text("ALTER TABLE departments ADD COLUMN hospital_id INTEGER"))
            conn.commit()
        
        try:
            # Check if hospital_id column exists in doctors
            conn.execute(text("SELECT hospital_id FROM doctors LIMIT 1"))
            print("hospital_id column already exists in doctors table")
        except Exception:
            print("Adding hospital_id column to doctors table...")
            conn.execute(text("ALTER TABLE doctors ADD COLUMN hospital_id INTEGER"))
            conn.commit()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()