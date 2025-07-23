from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.models.base import Base, AuditMixin

class Hospital(Base, AuditMixin):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum("active", "inactive", "pending", name="hospital_status"), default="pending")
    license_number = Column(String, nullable=True)
    established_year = Column(Integer, nullable=True)
    logo = Column(String, nullable=True)

    # Relationships
    admin = relationship("User", back_populates="managed_hospitals")
    departments = relationship("Department", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    appointments = relationship("Appointment", back_populates="hospital")