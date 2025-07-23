from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    hospital_id: int
    department_id: int
    appointment_date: date
    appointment_time: time
    duration_minutes: int = 30
    appointment_type: str
    status: str = "scheduled"
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    consultation_fee: Optional[float] = None
    booking_source: str


class AppointmentCreate(AppointmentBase):
    booking_reference: str


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    appointment_type: Optional[str] = None
    status: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    consultation_fee: Optional[float] = None
    cancelled_by: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None


class AppointmentInDBBase(AppointmentBase):
    id: int
    booking_reference: str
    cancelled_by: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Appointment(AppointmentInDBBase):
    pass