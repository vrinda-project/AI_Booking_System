from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Doctor, Department
from ..schemas import DoctorResponse, DepartmentResponse

router = APIRouter(prefix="/api/doctors", tags=["doctors"])

@router.get("/", response_model=List[DoctorResponse])
async def get_all_doctors(db: Session = Depends(get_db)):
    """Get all active doctors"""
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
    return doctors

@router.get("/by-department/{department_id}", response_model=List[DoctorResponse])
async def get_doctors_by_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Get doctors by department"""
    doctors = db.query(Doctor).filter(
        Doctor.department_id == department_id,
        Doctor.is_active == True
    ).all()
    return doctors

@router.get("/{doctor_id}/availability")
async def get_doctor_availability(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get doctor's availability schedule"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        return {"error": "Doctor not found"}
    
    return {"availability": doctor.availability}

@router.get("/departments", response_model=List[DepartmentResponse])
async def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).all()
    return departments