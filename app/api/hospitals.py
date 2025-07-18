from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Hospital, Department, Doctor, Appointment
from ..schemas.hospital import HospitalCreate, HospitalResponse, HospitalUpdate, HospitalStatistics
from datetime import datetime
from sqlalchemy import func

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])

# Helper function to verify token - disabled for testing
def verify_token():
    # Authentication disabled for testing
    return "test_token"

@router.get("/", response_model=List[HospitalResponse])
async def get_all_hospitals(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all hospitals with pagination, search and filtering"""
    skip = (page - 1) * limit
    query = db.query(Hospital)
    
    # Apply filters
    if search:
        query = query.filter(Hospital.name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Hospital.status == status)
    
    # Apply pagination
    hospitals = query.offset(skip).limit(limit).all()
    return hospitals

@router.get("/{hospital_id}", response_model=HospitalResponse)
async def get_hospital_by_id(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Get hospital by ID"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.post("/", response_model=HospitalResponse)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):
    """Create a new hospital"""
    hospital = Hospital(**hospital_data.dict())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

@router.put("/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db)
):
    """Update hospital information"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Update only provided fields
    update_data = hospital_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(hospital, key, value)
    
    hospital.updated_at = datetime.now()
    db.commit()
    db.refresh(hospital)
    return hospital

@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Delete a hospital"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # In a real app, you might want to soft delete or check for dependencies
    db.delete(hospital)
    db.commit()
    
    return {"message": "Hospital deleted successfully"}

@router.get("/{hospital_id}/statistics")
async def get_hospital_statistics(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """Get hospital statistics"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Get statistics
    total_departments = db.query(Department).filter(Department.hospital_id == hospital_id).count()
    total_doctors = db.query(Doctor).filter(Doctor.hospital_id == hospital_id).count()
    active_doctors = db.query(Doctor).filter(Doctor.hospital_id == hospital_id, Doctor.is_active == True).count()
    
    # Get appointment statistics
    total_appointments = db.query(Appointment).join(Doctor).filter(Doctor.hospital_id == hospital_id).count()
    upcoming_appointments = db.query(Appointment).join(Doctor).filter(
        Doctor.hospital_id == hospital_id,
        Appointment.appointment_datetime > datetime.now()
    ).count()
    
    return {
        "hospital_id": hospital_id,
        "hospital_name": hospital.name,
        "total_departments": total_departments,
        "total_doctors": total_doctors,
        "active_doctors": active_doctors,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments
    }