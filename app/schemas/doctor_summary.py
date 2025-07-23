from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoctorSummary(BaseModel):
    id: int
    full_name: str
    specialty: str
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True
        from_attributes = True