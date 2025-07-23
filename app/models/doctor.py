from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base, AuditMixin

class Doctor(Base, AuditMixin):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    specialization = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    consultation_fee = Column(Numeric(10, 2), nullable=True)
    languages_spoken = Column(String, nullable=True)
    awards_recognition = Column(String, nullable=True)
    biography = Column(String, nullable=True)
    availability = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    license_number = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    hospital = relationship("Hospital", back_populates="doctors")
    department = relationship("Department", back_populates="doctors", foreign_keys=[department_id])
    appointments = relationship("Appointment", back_populates="doctor")