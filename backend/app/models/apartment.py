"""Apartment model for condominium management."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as _sa_text
from sqlalchemy.orm import relationship

from app.models.base import Base


# Association table for many-to-many relationship between users and apartments
apartment_users = Table(
    "apartment_users",
    Base.metadata,
    Column("apartment_id", String(36), ForeignKey("apartments.id"), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
)


class Apartment(Base):
    __tablename__ = "apartments"
    
    id = Column(UUID(as_uuid=False), primary_key=True, server_default=_sa_text('gen_random_uuid()'))
    building_id = Column(UUID(as_uuid=False), ForeignKey("buildings.id"), nullable=False, index=True)
    unit_number = Column(String(50), nullable=False)
    floor = Column(Integer, nullable=True)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    square_meters = Column(Float, nullable=True)
    
    # Relationships
    building = relationship("Building", back_populates="apartments")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_apartments")
    tenant = relationship("User", foreign_keys=[tenant_id], back_populates="rented_apartments")
    residents = relationship(
        "User",
        secondary=apartment_users,
        back_populates="apartments"
    )
    reports = relationship("Report", back_populates="apartment", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="apartment", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Apartment(id={self.id}, unit={self.unit_number}, building={self.building_id})>"
    
    def __str__(self) -> str:
        return f"Unit {self.unit_number}"


# Composite index for common query patterns
Index("ix_apartments_building_unit", Apartment.building_id, Apartment.unit_number)
