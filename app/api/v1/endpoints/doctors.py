from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.doctor import Doctor as DoctorSchema, DoctorCreate, DoctorUpdate

router = APIRouter()


@router.get("/", response_model=List[DoctorSchema])
def read_doctors(
    db: Session = Depends(deps.get_db),
    hospital_id: int = None,
    department_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve doctors.
    """
    query = db.query(Doctor)
    
    if hospital_id:
        query = query.filter(Doctor.hospital_id == hospital_id)
    
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    
    # Filter by permissions
    if current_user.role == "hospital_admin":
        hospitals = db.query(Hospital).filter(Hospital.admin_id == current_user.id).all()
        hospital_ids = [h.id for h in hospitals]
        query = query.filter(Doctor.hospital_id.in_(hospital_ids))
    
    doctors = query.offset(skip).limit(limit).all()
    return doctors


@router.post("/", response_model=DoctorSchema)
def create_doctor(
    *,
    db: Session = Depends(deps.get_db),
    doctor_in: DoctorCreate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Create new doctor.
    """
    # Check if hospital exists and user has permission
    hospital = db.query(Hospital).filter(Hospital.id == doctor_in.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    if current_user.role == "hospital_admin" and hospital.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    doctor = Doctor(
        **doctor_in.dict(),
        created_by=str(current_user.id),
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/{doctor_id}", response_model=DoctorSchema)
def read_doctor(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get doctor by ID.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check permissions for hospital admins
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == doctor.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return doctor


@router.put("/{doctor_id}", response_model=DoctorSchema)
def update_doctor(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id: int,
    doctor_in: DoctorUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == doctor.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = doctor_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)
    
    doctor.updated_by = str(current_user.id)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}")
def delete_doctor(
    *,
    db: Session = Depends(deps.get_db),
    doctor_id: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete a doctor.
    """
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == doctor.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(doctor)
    db.commit()
    return {"status": "success"}