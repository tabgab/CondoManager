"""Apartment model for condominium management."""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    unit_number = Column(String(50), nullable=False)
    floor = Column(Integer, nullable=True)
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    building = relationship("Building", back_populates="apartments")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_apartments")
    tenant = relationship("User", foreign_keys=[tenant_id], back_populates="rented_apartments")
    reports = relationship("Report", back_populates="apartment")
    tasks = relationship("Task", back_populates="apartment")

    def __repr__(self) -> str:
        return f"<Apartment(id={self.id}, unit={self.unit_number}, building={self.building_id})>"

    def __str__(self) -> str:
        return f"Unit {self.unit_number}"
