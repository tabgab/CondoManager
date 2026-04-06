"""ReportMessage model for threaded conversations."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base


class ReportMessage(Base):
    """Message in a report thread."""
    __tablename__ = "report_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False, index=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    photo_urls = Column(String, nullable=True)  # JSON stored as string for SQLite compatibility
    is_internal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    report = relationship("Report", back_populates="messages")
    author = relationship("User", back_populates="report_messages")
