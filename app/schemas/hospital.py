from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.schemas.department_summary import DepartmentSummary
from app.schemas.doctor_summary import DoctorSummary


class HospitalBase(BaseModel):
    name: str
    address: str
    phone: str
    email: EmailStr
    website: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"
    license_number: Optional[str] = None
    established_year: Optional[int] = None
    logo: Optional[str] = None


class HospitalCreate(HospitalBase):
    admin_id: Optional[int] = None


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    description: Optional[str] = None
    admin_id: Optional[int] = None
    status: Optional[str] = None
    license_number: Optional[str] = None
    established_year: Optional[int] = None
    logo: Optional[str] = None


class HospitalInDBBase(HospitalBase):
    id: int
    admin_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class Hospital(HospitalInDBBase):
    pass


class HospitalDetail(HospitalInDBBase):
    departments: Optional[List[DepartmentSummary]] = None
    doctors: Optional[List[DoctorSummary]] = None