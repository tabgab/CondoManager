"""Building model for condominium management."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id])
    apartments = relationship("Apartment", back_populates="building", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="building")
    tasks = relationship("Task", back_populates="building")
    recurring_tasks = relationship("RecurringTask", back_populates="building")

    def __repr__(self) -> str:
        return f"<Building(id={self.id}, name={self.name})>"

    def __str__(self) -> str:
        return f"{self.name} - {self.address}"
