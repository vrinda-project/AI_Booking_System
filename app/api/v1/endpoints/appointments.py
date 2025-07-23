from typing import Any, List
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api import deps
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.appointment import Appointment as AppointmentSchema, AppointmentCreate, AppointmentUpdate

router = APIRouter()


@router.get("/", response_model=List[AppointmentSchema])
def read_appointments(
    db: Session = Depends(deps.get_db),
    hospital_id: int = None,
    doctor_id: int = None,
    patient_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve appointments.
    """
    query = db.query(Appointment)
    
    # Apply filters
    if hospital_id:
        query = query.filter(Appointment.hospital_id == hospital_id)
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    # Apply permission filters
    if current_user.role == "hospital_admin":
        hospitals = db.query(Hospital).filter(Hospital.admin_id == current_user.id).all()
        hospital_ids = [h.id for h in hospitals]
        query = query.filter(Appointment.hospital_id.in_(hospital_ids))
    elif current_user.role == "doctor":
        if not current_user.doctor_profile:
            raise HTTPException(status_code=400, detail="User is not a doctor")
        query = query.filter(Appointment.doctor_id == current_user.doctor_profile.id)
    elif current_user.role == "patient":
        if not current_user.patient_profile:
            raise HTTPException(status_code=400, detail="User is not a patient")
        query = query.filter(Appointment.patient_id == current_user.patient_profile.id)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_in: AppointmentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new appointment.
    """
    # Check for double booking
    existing_appointment = db.query(Appointment).filter(
        and_(
            Appointment.doctor_id == appointment_in.doctor_id,
            Appointment.appointment_date == appointment_in.appointment_date,
            Appointment.appointment_time == appointment_in.appointment_time,
            Appointment.status.in_(["scheduled", "confirmed"])
        )
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this time"
        )
    
    # Generate unique booking reference
    booking_reference = f"APPT-{uuid.uuid4().hex[:8].upper()}"
    
    appointment = Appointment(
        **appointment_in.dict(),
        booking_reference=booking_reference,
        created_by=str(current_user.id),
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentSchema)
def read_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get appointment by ID.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "doctor":
        if not current_user.doctor_profile or current_user.doctor_profile.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "patient":
        if not current_user.patient_profile or current_user.patient_profile.id != appointment.patient_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "doctor":
        if not current_user.doctor_profile or current_user.doctor_profile.id != appointment.doctor_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "patient":
        if not current_user.patient_profile or current_user.patient_profile.id != appointment.patient_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check for double booking if changing date/time
    if appointment_in.appointment_date or appointment_in.appointment_time:
        new_date = appointment_in.appointment_date or appointment.appointment_date
        new_time = appointment_in.appointment_time or appointment.appointment_time
        
        existing_appointment = db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == appointment.doctor_id,
                Appointment.appointment_date == new_date,
                Appointment.appointment_time == new_time,
                Appointment.status.in_(["scheduled", "confirmed"]),
                Appointment.id != appointment_id
            )
        ).first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=400,
                detail="Doctor already has an appointment at this time"
            )
    
    # Handle cancellation
    if appointment_in.status == "cancelled" and appointment.status != "cancelled":
        appointment_in.cancelled_by = str(current_user.id)
        appointment_in.cancelled_at = datetime.utcnow()
    
    update_data = appointment_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    appointment.updated_by = str(current_user.id)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    *,
    db: Session = Depends(deps.get_db),
    appointment_id: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete an appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == appointment.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(appointment)
    db.commit()
    return {"status": "success"}