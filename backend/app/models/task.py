"""Task model for work assignment and tracking."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Task(Base):
    """Task model for work assignment to employees."""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, server_default='pending')
    priority = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True)
    progress = Column(Integer, nullable=False, server_default='0')
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    apartment_id = Column(UUID(as_uuid=False), ForeignKey("apartments.id", ondelete="SET NULL"), nullable=True)
    report_id = Column(UUID(as_uuid=False), ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)
    recurring_task_id = Column(UUID(as_uuid=False), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="tasks_created")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tasks_assigned")
    verified_by = relationship("User", foreign_keys=[verified_by_id], back_populates="tasks_verified")
    building = relationship("Building", back_populates="tasks")
    apartment = relationship("Apartment", back_populates="tasks")
    report = relationship("Report", back_populates="tasks")
    updates = relationship("TaskUpdate", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
