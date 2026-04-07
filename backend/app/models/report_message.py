"""ReportMessage model for threaded conversations."""
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class ReportMessage(Base):
    """Message in a report thread."""
    __tablename__ = "report_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    report_id = Column(UUID(as_uuid=False), ForeignKey("reports.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    photo_urls = Column(String, nullable=True)  # JSON stored as string for SQLite compatibility
    is_internal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    report = relationship("Report", back_populates="messages")
    author = relationship("User", back_populates="report_messages")
