"""Task schemas."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    building_id: Optional[str] = None
    apartment_id: Optional[str] = None
    report_id: Optional[str] = None


class TaskCreate(TaskBase):
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    progress: int = 0
    created_by_id: Optional[str] = None
    assignee_id: Optional[str] = None
    verified_by_id: Optional[str] = None
    recurring_task_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    skip: int = 0
    limit: int = 100


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class TaskCompletion(BaseModel):
    progress: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class TaskVerification(BaseModel):
    approved: bool = True
    notes: Optional[str] = None
