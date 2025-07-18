from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter(prefix="/api/db-view", tags=["db-view"])

@router.get("/hospital-department")
async def view_hospital_department_table(db: Session = Depends(get_db)):
    """View raw hospital_department table data"""
    query = text("SELECT hospital_id, department_id FROM hospital_department")
    result = db.execute(query).fetchall()
    
    # Convert to list of dictionaries
    data = [{"hospital_id": row[0], "department_id": row[1]} for row in result]
    
    # Add hospital and department names for readability
    for item in data:
        # Get hospital name
        hospital_query = text("SELECT name FROM hospitals WHERE id = :id")
        hospital_name = db.execute(hospital_query, {"id": item["hospital_id"]}).scalar()
        item["hospital_name"] = hospital_name
        
        # Get department name
        dept_query = text("SELECT name FROM departments WHERE id = :id")
        dept_name = db.execute(dept_query, {"id": item["department_id"]}).scalar()
        item["department_name"] = dept_name
    
    return {
        "message": "Raw hospital_department table data",
        "data": data
    }

@router.get("/tables")
async def list_database_tables(db: Session = Depends(get_db)):
    """List all tables in the database"""
    query = text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    result = db.execute(query).fetchall()
    tables = [row[0] for row in result]
    
    return {
        "message": "Database tables",
        "tables": tables
    }