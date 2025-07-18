from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str = Field(default="Cardiology", description="Department name")
    description: Optional[str] = Field(default="Heart and cardiovascular conditions", description="Department description")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    description: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: int
    
    class Config:
        from_attributes = True

class DoctorBase(BaseModel):
    name: str = Field(default="Dr. John Smith", description="Doctor's full name")
    specialty: str = Field(default="Cardiologist", description="Doctor's specialty")
    department_id: int = Field(default=1, description="ID of the department")
    hospital_id: Optional[int] = Field(default=None, description="ID of the hospital")
    is_active: bool = Field(default=True, description="Whether the doctor is active")

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(DoctorBase):
    name: Optional[str] = None
    specialty: Optional[str] = None
    department_id: Optional[int] = None
    hospital_id: Optional[int] = None
    is_active: Optional[bool] = None

class DoctorResponse(DoctorBase):
    id: int
    
    class Config:
        from_attributes = True