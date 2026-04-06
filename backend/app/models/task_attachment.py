"""TaskAttachment model for file/photo uploads."""
from uuid import uuid4
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class FileType(str, Enum):
    """File type enumeration."""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"


class TaskAttachment(Base):
    """Attachment for a task (photos, documents, audio)."""
    __tablename__ = "task_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    
    file_type = Column(String(20), nullable=False, default=FileType.IMAGE)
    file_url = Column(String(500), nullable=False)  # Cloudinary URL
    file_name = Column(String(255), nullable=False)
    
    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploaded_by = relationship("User", back_populates="task_attachments")
