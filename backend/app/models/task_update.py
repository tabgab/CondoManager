"""TaskUpdate model for progress tracking and concerns."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskUpdate(Base):
    """Update or concern posted on a task."""
    __tablename__ = "task_updates"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    content = Column(Text, nullable=False)
    update_type = Column(String(50), nullable=False, server_default='comment')
    task_id = Column(UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="updates")
    author = relationship("User", back_populates="task_updates")
