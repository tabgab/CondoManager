"""TaskUpdate model for progress tracking and concerns."""
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskUpdate(Base):
    """Update or concern posted on a task."""
    __tablename__ = "task_updates"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    task_id = Column(UUID(as_uuid=False), ForeignKey("tasks.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    
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
