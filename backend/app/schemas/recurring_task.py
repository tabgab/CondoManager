"""Pydantic schemas for RecurringTask model."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.models.recurring_task import RecurringFrequency


class RecurringTaskBase(BaseModel):
    """Base schema for recurring task data."""
    template_title: str = Field(..., min_length=1, max_length=255)
    template_description: Optional[str] = None
    frequency: RecurringFrequency
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    is_active: Optional[bool] = True
    assignee_id: Optional[UUID] = None
    building_id: Optional[UUID] = None


class RecurringTaskCreate(RecurringTaskBase):
    """Schema for creating a new recurring task."""
    pass


class RecurringTaskUpdate(BaseModel):
    """Schema for updating a recurring task."""
    template_title: Optional[str] = Field(None, min_length=1, max_length=255)
    template_description: Optional[str] = None
    frequency: Optional[RecurringFrequency] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    hour: Optional[int] = Field(None, ge=0, le=23)
    is_active: Optional[bool] = None
    assignee_id: Optional[UUID] = None
    building_id: Optional[UUID] = None


class RecurringTaskToggle(BaseModel):
    """Schema for toggling active status."""
    is_active: bool


class RecurringTaskResponse(RecurringTaskBase):
    """Schema for recurring task response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_by_id: UUID
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
