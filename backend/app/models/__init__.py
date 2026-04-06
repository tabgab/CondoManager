"""SQLAlchemy models for CondoManager."""
from app.models.base import Base, engine, AsyncSessionLocal, get_db
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.apartment import Apartment, apartment_users
from app.models.report import Report, ReportCategory, ReportStatus, ReportPriority
from app.models.report_message import ReportMessage
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_update import TaskUpdate
from app.models.task_attachment import TaskAttachment, FileType
from app.models.recurring_task import RecurringTask, TaskFrequency
from app.models.push_subscription import PushSubscription

__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "User",
    "UserRole",
    "Building",
    "Apartment",
    "apartment_users",
    "Report",
    "ReportCategory",
    "ReportStatus",
    "ReportPriority",
    "ReportMessage",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "TaskUpdate",
    "TaskAttachment",
    "FileType",
    "RecurringTask",
    "TaskFrequency",
    "PushSubscription",
]
