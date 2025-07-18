from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    doctors = relationship("Doctor", back_populates="department")
    hospitals = relationship("Hospital", secondary="hospital_department", back_populates="departments")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    availability = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    department = relationship("Department", back_populates="doctors")
    hospital = relationship("Hospital", back_populates="doctors")
    time_slots = relationship("TimeSlot", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")