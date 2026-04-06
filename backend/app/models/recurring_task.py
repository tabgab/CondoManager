"""RecurringTask model for scheduled repeating tasks."""
from uuid import uuid4
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskFrequency(str, Enum):
    """Frequency for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Alias for backward compatibility with schema imports
RecurringFrequency = TaskFrequency


class RecurringTask(Base):
    """Template for recurring scheduled tasks."""
    __tablename__ = "recurring_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    template_title = Column(String(255), nullable=False)
    template_description = Column(Text, nullable=True)
    
    assignee_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=True, index=True)
    
    frequency = Column(String(20), nullable=False, default=TaskFrequency.WEEKLY)
    day_of_week = Column(Integer, nullable=True)  # 0-6 for weekly (0=Monday in Python, but configurable)
    day_of_month = Column(Integer, nullable=True)  # 1-31 for monthly
    hour = Column(Integer, nullable=False, default=9)  # Hour when task should be created (0-23)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="recurring_tasks_assigned")
    building = relationship("Building", back_populates="recurring_tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="recurring_tasks_created")
