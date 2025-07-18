"""
Script to run the hospital_department migration
"""
import os
from sqlalchemy import create_engine, text
from app.database import engine

def run_migration():
    print("Running hospital_department migration...")
    
    # Read SQL file
    with open('add_hospital_department_table.sql', 'r') as f:
        sql = f.read()
    
    # Execute SQL
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()