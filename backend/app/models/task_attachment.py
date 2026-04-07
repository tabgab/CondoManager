"""TaskAttachment model for file/photo uploads."""

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class TaskAttachment(Base):
    """Attachment for a task (photos, documents, audio)."""
    __tablename__ = "task_attachments"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    task_id = Column(UUID(as_uuid=False), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploaded_by = relationship("User", back_populates="task_attachments")
