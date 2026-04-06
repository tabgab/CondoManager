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
    description: str = Field(..., min_length=1)
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    building_id: Optional[str] = None
    apartment_id: Optional[str] = None
    report_id: Optional[str] = None


class TaskCreate(TaskBase):
    assignee_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: TaskStatus
    created_by_id: str
    assignee_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    verified_by_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    skip: int = 0
    limit: int = 100


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    percentage_complete: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class TaskCompletion(BaseModel):
    percentage_complete: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class TaskVerification(BaseModel):
    approved: bool = True
    rejection_reason: Optional[str] = None
