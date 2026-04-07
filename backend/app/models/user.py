"""User model with role-based access control."""
import os
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


# Forward references for type hints
if False:  # noqa: F401
    from app.models.apartment import Apartment


class UserRole(str, Enum):
    """User role enumeration."""
    SUPER_ADMIN = "super_admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    OWNER = "owner"
    TENANT = "tenant"


class User(Base):
    """User model for all roles in the condominium management system."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.TENANT,
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    telegram_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships with apartments (many-to-many via apartment_users table)
    apartments: Mapped[list["Apartment"]] = relationship(
        "Apartment",
        secondary="apartment_users",
        back_populates="residents"
    )
    owned_apartments: Mapped[list["Apartment"]] = relationship(
        "Apartment",
        foreign_keys="Apartment.owner_id",
        back_populates="owner"
    )
    rented_apartments: Mapped[list["Apartment"]] = relationship(
        "Apartment",
        foreign_keys="Apartment.tenant_id",
        back_populates="tenant"
    )
    
    # Relationships with reports
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        foreign_keys="Report.reporter_id",
        back_populates="reporter"
    )
    report_messages: Mapped[list["ReportMessage"]] = relationship(
        "ReportMessage",
        back_populates="author"
    )
    
    # Relationships with tasks
    tasks_created: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.created_by_id",
        back_populates="created_by"
    )
    tasks_assigned: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.assignee_id",
        back_populates="assignee"
    )
    tasks_verified: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.verified_by_id",
        back_populates="verified_by"
    )
    task_updates: Mapped[list["TaskUpdate"]] = relationship(
        "TaskUpdate",
        back_populates="author"
    )
    task_attachments: Mapped[list["TaskAttachment"]] = relationship(
        "TaskAttachment",
        back_populates="uploaded_by"
    )
    
    # Relationships with recurring tasks
    recurring_tasks_assigned: Mapped[list["RecurringTask"]] = relationship(
        "RecurringTask",
        foreign_keys="RecurringTask.assignee_id",
        back_populates="assignee"
    )
    recurring_tasks_created: Mapped[list["RecurringTask"]] = relationship(
        "RecurringTask",
        foreign_keys="RecurringTask.created_by_id",
        back_populates="created_by"
    )
    
    # Relationships with push subscriptions
    push_subscriptions: Mapped[list["PushSubscription"]] = relationship(
        "PushSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, email={self.email}, "
            f"role={self.role}, is_active={self.is_active})>"
        )
    
    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"
