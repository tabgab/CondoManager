"""Report model for condominium issue reporting."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Report(Base):
    """Report model for apartment issues."""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    priority = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, server_default='pending')
    photo_url = Column(String(500), nullable=True)
    submitted_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    apartment_id = Column(UUID(as_uuid=False), ForeignKey("apartments.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    submitted_by = relationship("User", foreign_keys=[submitted_by_id], back_populates="reports")
    building = relationship("Building", back_populates="reports")
    apartment = relationship("Apartment", back_populates="reports")
    messages = relationship("ReportMessage", back_populates="report", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="report")
