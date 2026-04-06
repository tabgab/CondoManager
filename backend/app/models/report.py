"""Report model for condominium issue reporting."""
from uuid import uuid4
from sqlalchemy import Column, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class ReportCategory(str, Enum):
    """Report category enum."""
    MAINTENANCE = "maintenance"
    CLEANING = "cleaning"
    SAFETY = "safety"
    NOISE = "noise"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Report status enum."""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    TASK_CREATED = "task_created"
    REJECTED = "rejected"
    RESOLVED = "resolved"
    DELETED = "deleted"


class ReportPriority(str, Enum):
    """Report priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Report(Base):
    """Report model for apartment issues."""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    apartment_id = Column(String(36), ForeignKey("apartments.id"), nullable=True, index=True)
    building_id = Column(String(36), ForeignKey("buildings.id"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=False, default=ReportCategory.OTHER)
    status = Column(String(20), nullable=False, default=ReportStatus.PENDING)
    priority = Column(String(20), nullable=False, default=ReportPriority.MEDIUM)
    
    photo_urls = Column(JSON, default=list)
    assigned_manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports")
    apartment = relationship("Apartment", back_populates="reports")
    building = relationship("Building", back_populates="reports")
    assigned_manager = relationship("User", foreign_keys=[assigned_manager_id])
    messages = relationship("ReportMessage", back_populates="report", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="report", cascade="all, delete-orphan")
