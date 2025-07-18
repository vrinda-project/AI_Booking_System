from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_datetime: datetime
    notes: Optional[str] = None

class AppointmentCreate(BaseModel):
    patient_phone: str
    doctor_id: int
    appointment_datetime: datetime
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True