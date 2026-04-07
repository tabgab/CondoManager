"""ReportMessage model for threaded conversations."""

from sqlalchemy import Column, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class ReportMessage(Base):
    """Message in a report thread."""
    __tablename__ = "report_messages"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    content = Column(Text, nullable=False)
    report_id = Column(UUID(as_uuid=False), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    report = relationship("Report", back_populates="messages")
    sender = relationship("User", back_populates="report_messages")
