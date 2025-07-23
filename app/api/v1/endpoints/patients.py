from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import Patient as PatientSchema, PatientCreate, PatientUpdate

router = APIRouter()


@router.get("/", response_model=List[PatientSchema])
def read_patients(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Retrieve patients.
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.post("/", response_model=PatientSchema)
def create_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_in: PatientCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new patient.
    """
    patient = Patient(
        **patient_in.dict(),
        created_by=str(current_user.id),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientSchema)
def read_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get patient by ID.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Patients can only access their own records
    if current_user.role == "patient" and (not current_user.patient_profile or current_user.patient_profile.id != patient_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return patient


@router.put("/{patient_id}", response_model=PatientSchema)
def update_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    patient_in: PatientUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a patient.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Patients can only update their own records
    if current_user.role == "patient" and (not current_user.patient_profile or current_user.patient_profile.id != patient_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = patient_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    patient.updated_by = str(current_user.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    *,
    db: Session = Depends(deps.get_db),
    patient_id: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete a patient.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return {"status": "success"}