from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Appointment
from ..schemas import AppointmentCreate, AppointmentResponse
from ..services import BookingService

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

@router.get("/availability")
async def check_availability(
    doctor_id: int,
    date: str,
    db: Session = Depends(get_db)
):
    """Check doctor availability for a specific date"""
    booking_service = BookingService(db)
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        slots = booking_service.get_available_slots(doctor_id, date_obj)
        return [{"start_time": slot.start_time, "end_time": slot.end_time} for slot in slots]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@router.post("/book", response_model=AppointmentResponse)
async def book_appointment(
    patient_phone: str,
    doctor_id: int,
    appointment_datetime: datetime,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Book a new appointment"""
    booking_service = BookingService(db)
    try:
        appointment = booking_service.book_appointment(
            patient_phone, doctor_id, appointment_datetime, notes
        )
        return appointment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/patient/{phone}")
async def get_patient_appointments(
    phone: str,
    db: Session = Depends(get_db)
):
    """Get all appointments for a patient"""
    appointments = db.query(Appointment).join(Appointment.patient).filter(
        Appointment.patient.has(phone=phone)
    ).all()
    return appointments

@router.put("/{appointment_id}/reschedule")
async def reschedule_appointment(
    appointment_id: int,
    new_datetime: datetime,
    db: Session = Depends(get_db)
):
    """Reschedule an existing appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.appointment_datetime = new_datetime
    appointment.status = "rescheduled"
    db.commit()
    
    return {"message": "Appointment rescheduled successfully"}

@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = "cancelled"
    db.commit()
    
    return {"message": "Appointment cancelled successfully"}