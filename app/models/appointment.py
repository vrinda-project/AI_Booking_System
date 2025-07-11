from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient")
    doctor = relationship("Doctor", back_populates="appointments")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_available = Column(Boolean, default=True)
    
    doctor = relationship("Doctor", back_populates="time_slots")