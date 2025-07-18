"""
Simple script to run SQL directly
"""
import os
from sqlalchemy import create_engine, text
from app.database import engine

def run_sql():
    print("Running SQL script...")
    
    # Read SQL file
    with open('add_hospital_columns.sql', 'r') as f:
        sql = f.read()
    
    # Execute SQL
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("SQL executed successfully!")

if __name__ == "__main__":
    run_sql()