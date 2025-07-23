from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DepartmentSummary(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    head_doctor_id: Optional[int] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True
        from_attributes = True