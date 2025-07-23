from sqlalchemy import Column, DateTime, String, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuditMixin:
    """Mixin for audit fields that will be added to all tables"""
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_ip = Column(String, nullable=True)
    updated_ip = Column(String, nullable=True)