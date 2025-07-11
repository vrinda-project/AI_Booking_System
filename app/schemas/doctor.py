from pydantic import BaseModel
from typing import Optional, Dict

class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    department_id: int
    availability: Optional[Dict] = {}
    is_active: bool
    department: Optional[DepartmentResponse] = None
    
    class Config:
        from_attributes = True