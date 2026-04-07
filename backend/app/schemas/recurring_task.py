"""Pydantic schemas for RecurringTask model."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RecurringTaskBase(BaseModel):
    """Base schema for recurring task data."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    frequency: str = Field(..., description="daily, weekly, or monthly")
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    is_active: Optional[bool] = True
    assignee_id: Optional[str] = None
    building_id: Optional[str] = None


class RecurringTaskCreate(RecurringTaskBase):
    """Schema for creating a new recurring task."""
    pass


class RecurringTaskUpdate(BaseModel):
    """Schema for updating a recurring task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    frequency: Optional[str] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    is_active: Optional[bool] = None
    assignee_id: Optional[str] = None
    building_id: Optional[str] = None


class RecurringTaskToggle(BaseModel):
    """Schema for toggling active status."""
    is_active: bool


class RecurringTaskResponse(RecurringTaskBase):
    """Schema for recurring task response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_by_id: Optional[str] = None
    last_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Optional related data
    assignee_name: Optional[str] = None
    building_name: Optional[str] = None


class RecurringTaskListResponse(BaseModel):
    """Schema for list of recurring tasks response."""
    items: list[RecurringTaskResponse]
    total: int
    skip: int
    limit: int
