"""Task model for work assignment and tracking."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model for work assignment to employees."""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    status = Column(String(20), nullable=False, default=TaskStatus.PENDING)
    priority = Column(String(20), nullable=False, default=TaskPriority.NORMAL)
    
    created_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    assignee_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True, index=True)
    
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id"), nullable=True, index=True)
    apartment_id = Column(UUID(as_uuid=False), ForeignKey("apartments.id"), nullable=True, index=True)
    report_id = Column(UUID(as_uuid=False), ForeignKey("reports.id"), nullable=True, index=True)
    
    estimated_hours = Column(Float, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    verified_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="tasks_created")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tasks_assigned")
    verified_by = relationship("User", foreign_keys=[verified_by_id], back_populates="tasks_verified")
    
    building = relationship("Building", back_populates="tasks")
    apartment = relationship("Apartment", back_populates="tasks")
    report = relationship("Report", back_populates="tasks")
    
    updates = relationship("TaskUpdate", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
