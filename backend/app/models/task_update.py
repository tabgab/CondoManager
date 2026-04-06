"""TaskUpdate model for progress tracking and concerns."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, Index
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskUpdate(Base):
    """Update or concern posted on a task."""
    __tablename__ = "task_updates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    is_concern = Column(Boolean, default=False, nullable=False)
    requires_manager_attention = Column(Boolean, default=False, nullable=False)
    percentage_complete = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="updates")
    author = relationship("User", back_populates="task_updates")


# Index for querying updates by task
Index("ix_task_updates_task_created", TaskUpdate.task_id, TaskUpdate.created_at.desc())
