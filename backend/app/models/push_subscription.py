"""Push subscription model for Web Push notifications."""

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class PushSubscription(Base):
    """Model for storing browser push notification subscriptions."""
    __tablename__ = "push_subscriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String(500), nullable=False, unique=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    device_info = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="push_subscriptions")

    def __repr__(self) -> str:
        return f"<PushSubscription(id={self.id}, user_id={self.user_id})>"
