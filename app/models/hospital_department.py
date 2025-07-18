from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..database import Base

# Many-to-many relationship table between hospitals and departments
hospital_department = Table(
    "hospital_department",
    Base.metadata,
    Column("hospital_id", Integer, ForeignKey("hospitals.id"), primary_key=True),
    Column("department_id", Integer, ForeignKey("departments.id"), primary_key=True)
)