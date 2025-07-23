from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship

from app.models.base import Base, AuditMixin

class Appointment(Base, AuditMixin):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(Enum("consultation", "follow_up", "emergency", "checkup", name="appointment_type"))
    status = Column(Enum("scheduled", "confirmed", "cancelled", "completed", "no_show", name="appointment_status"))
    symptoms = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    consultation_fee = Column(Numeric(10, 2), nullable=True)
    booking_source = Column(Enum("web", "phone", "ai_voice", "walk_in", name="booking_source"))
    booking_reference = Column(String, unique=True, nullable=False)
    cancelled_by = Column(String, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    hospital = relationship("Hospital", back_populates="appointments")
    department = relationship("Department", back_populates="appointments")