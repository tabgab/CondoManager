"""Building model for condominium management."""
from uuid import uuid4

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=False, default="Hungary")
    description = Column(Text, nullable=True)
    
    # Relationships
    apartments = relationship("Apartment", back_populates="building", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="building", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="building", cascade="all, delete-orphan")
    recurring_tasks = relationship("RecurringTask", back_populates="building", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Building(id={self.id}, name={self.name}, city={self.city})>"
    
    def __str__(self) -> str:
        return f"{self.name} - {self.address}, {self.city}"
