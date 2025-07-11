from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class PatientBase(BaseModel):
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    preferences: Optional[Dict] = {}

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True