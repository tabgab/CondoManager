"""RecurringTask model for scheduled repeating tasks."""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class RecurringTask(Base):
    """Template for recurring scheduled tasks."""
    __tablename__ = "recurring_tasks"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    priority = Column(String(50), nullable=True)
    frequency = Column(String(50), nullable=False)
    day_of_week = Column(Integer, nullable=True)
    day_of_month = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='true')
    assignee_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    created_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="recurring_tasks_assigned")
    building = relationship("Building", back_populates="recurring_tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="recurring_tasks_created")
