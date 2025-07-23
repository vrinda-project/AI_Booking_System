from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class DoctorBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    specialty: str
    department_id: int
    hospital_id: int
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    languages_spoken: Optional[str] = None
    awards_recognition: Optional[str] = None
    biography: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None
    is_active: bool = True
    license_number: Optional[str] = None


class DoctorCreate(DoctorBase):
    user_id: Optional[int] = None


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    department_id: Optional[int] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    languages_spoken: Optional[str] = None
    awards_recognition: Optional[str] = None
    biography: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    license_number: Optional[str] = None


class DoctorInDBBase(DoctorBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Doctor(DoctorInDBBase):
    pass