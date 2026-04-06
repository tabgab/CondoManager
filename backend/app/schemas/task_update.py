"""Task update schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskUpdateCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_concern: bool = False
    requires_manager_attention: bool = False
    percentage_complete: Optional[int] = Field(None, ge=0, le=100)


class TaskUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    task_id: str
    author_id: str
    content: str
    is_concern: bool
    requires_manager_attention: bool
    percentage_complete: Optional[int]
    created_at: datetime


class TaskUpdateListResponse(BaseModel):
    items: list[TaskUpdateResponse]
    total: int
    skip: int = 0
    limit: int = 100
