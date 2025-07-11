from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_phone = Column(String, nullable=False)
    session_data = Column(JSON, default={})
    status = Column(String, default="active")  # active, completed, abandoned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    rating = Column(Integer)  # 1-5 scale
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    appointment = relationship("Appointment")