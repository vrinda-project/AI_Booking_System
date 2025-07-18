from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Hospital, Department, Doctor

router = APIRouter(prefix="/api/hospital-assignments", tags=["hospital-assignments"])

@router.post("/assign-department")
async def assign_department_to_hospital(
    hospital_id: int,
    department_id: int,
    db: Session = Depends(get_db)
):
    """Assign a department to a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if already assigned
    if department in hospital.departments:
        return {"message": "Department already assigned to this hospital"}
    
    # Add department to hospital
    hospital.departments.append(department)
    db.commit()
    
    return {"message": f"Department assigned to hospital successfully"}

@router.post("/assign-doctor")
async def assign_doctor_to_hospital(
    hospital_id: int,
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Assign a doctor to a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    doctor.hospital_id = hospital_id
    db.commit()
    
    return {"message": f"Doctor assigned to hospital successfully"}