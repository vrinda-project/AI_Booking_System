from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Hospital, Department, Doctor

router = APIRouter(prefix="/api/hospital-details", tags=["hospital-details"])

@router.get("/")
async def get_all_hospitals_with_details(db: Session = Depends(get_db)):
    """Get all hospitals with their departments and doctors"""
    hospitals = db.query(Hospital).all()
    
    result = []
    for hospital in hospitals:
        # Get departments using many-to-many relationship
        departments = hospital.departments
        dept_list = []
        
        for dept in departments:
            # Get doctors in this department and hospital
            doctors = db.query(Doctor).filter(
                Doctor.department_id == dept.id,
                Doctor.hospital_id == hospital.id
            ).all()
            
            dept_list.append({
                "id": dept.id,
                "name": dept.name,
                "description": dept.description,
                "doctors": [
                    {
                        "id": doc.id,
                        "name": doc.name,
                        "specialty": doc.specialty,
                        "is_active": doc.is_active
                    }
                    for doc in doctors
                ]
            })
        
        result.append({
            "id": hospital.id,
            "name": hospital.name,
            "address": hospital.address,
            "phone": hospital.phone,
            "email": hospital.email,
            "status": hospital.status,
            "departments": dept_list,
            "total_departments": len(dept_list),
            "total_doctors": sum(len(dept["doctors"]) for dept in dept_list)
        })
    
    return result

@router.get("/{hospital_id}")
async def get_hospital_details(hospital_id: int, db: Session = Depends(get_db)):
    """Get details for a specific hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get departments using many-to-many relationship
    departments = hospital.departments
    dept_list = []
    
    for dept in departments:
        # Get doctors in this department and hospital
        doctors = db.query(Doctor).filter(
            Doctor.department_id == dept.id,
            Doctor.hospital_id == hospital.id
        ).all()
        
        dept_list.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "doctors": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "specialty": doc.specialty,
                    "is_active": doc.is_active
                }
                for doc in doctors
            ]
        })
    
    return {
        "id": hospital.id,
        "name": hospital.name,
        "address": hospital.address,
        "phone": hospital.phone,
        "email": hospital.email,
        "status": hospital.status,
        "departments": dept_list,
        "total_departments": len(dept_list),
        "total_doctors": sum(len(dept["doctors"]) for dept in dept_list)
    }