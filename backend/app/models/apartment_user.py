"""ApartmentUser association model for many-to-many apartment-user relationships."""

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


class ApartmentUser(Base):
    """Association model linking users to apartments with a role (owner/tenant)."""

    __tablename__ = "apartment_users"
    __table_args__ = (
        UniqueConstraint('apartment_id', 'user_id', 'role', name='uq_apartment_user_role'),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    apartment_id = Column(UUID(as_uuid=False), ForeignKey("apartments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'owner' or 'tenant'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    apartment = relationship("Apartment", back_populates="users")
    user = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<ApartmentUser(id={self.id}, apartment={self.apartment_id}, user={self.user_id}, role={self.role})>"
