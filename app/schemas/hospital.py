from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class HospitalBase(BaseModel):
    name: str = Field(default="City General Hospital", description="Hospital name")
    address: str = Field(default="123 Main Street, Cityville", description="Hospital address")
    phone: str = Field(default="+1 (555) 123-4567", description="Contact phone number")
    email: str = Field(default="admin@cityhospital.com", description="Contact email address")
    admin_id: str = Field(default="admin123", description="ID of the hospital administrator")
    status: Optional[str] = Field(default="active", description="Hospital status (active, inactive, pending)")

class HospitalCreate(HospitalBase):
    """Schema for creating a new hospital"""
    
    class Config:
        schema_extra = {
            "example": {
                "name": "City General Hospital",
                "address": "123 Main Street, Cityville",
                "phone": "+1 (555) 123-4567",
                "email": "admin@cityhospital.com",
                "admin_id": "admin123",
                "status": "active"
            }
        }

class HospitalUpdate(HospitalBase):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    admin_id: Optional[str] = None
    status: Optional[str] = None

class HospitalResponse(HospitalBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class HospitalStatistics(BaseModel):
    hospital_id: int
    hospital_name: str
    total_departments: int
    total_doctors: int
    active_doctors: int
    total_appointments: int
    upcoming_appointments: int