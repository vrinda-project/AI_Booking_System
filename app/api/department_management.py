from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Department, Doctor
from ..schemas.doctor_department import DepartmentCreate, DepartmentUpdate, DepartmentResponse

router = APIRouter(prefix="/api/department-management", tags=["department-management"])

@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new department"""
    department = Department(**department_data.dict())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """Update department information"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Update only provided fields
    update_data = department_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(department, key, value)
    
    db.commit()
    db.refresh(department)
    return department

@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Delete a department"""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if there are doctors in this department
    doctors_count = db.query(Doctor).filter(Doctor.department_id == department_id).count()
    if doctors_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete department with {doctors_count} doctors. Reassign doctors first."
        )
    
    db.delete(department)
    db.commit()
    
    return {"message": "Department deleted successfully"}