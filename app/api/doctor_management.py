from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Doctor, Department
from ..schemas.doctor_department import DoctorCreate, DoctorUpdate, DoctorResponse

router = APIRouter(prefix="/api/doctor-management", tags=["doctor-management"])

@router.post("/doctors", response_model=DoctorResponse)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db)
):
    """Create a new doctor"""
    # Check if department exists
    department = db.query(Department).filter(Department.id == doctor_data.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    doctor = Doctor(**doctor_data.dict())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.put("/doctors/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db)
):
    """Update doctor information"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if department exists if provided
    if doctor_data.department_id is not None:
        department = db.query(Department).filter(Department.id == doctor_data.department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    
    # Update only provided fields
    update_data = doctor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/doctors/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Delete a doctor"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check for dependencies (appointments, etc.) in a real app
    db.delete(doctor)
    db.commit()
    
    return {"message": "Doctor deleted successfully"}