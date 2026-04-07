"""Task update schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskUpdateCreate(BaseModel):
    content: str = Field(..., min_length=1)
    update_type: str = "comment"


class TaskUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    author_id: Optional[str] = None
    content: str
    update_type: str = "comment"
    created_at: datetime
    updated_at: datetime


class TaskUpdateListResponse(BaseModel):
    items: list[TaskUpdateResponse]
    total: int
    skip: int = 0
    limit: int = 100
