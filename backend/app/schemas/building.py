"""Building Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BuildingCreate(BaseModel):
    """Schema for creating a building."""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    manager_id: Optional[str] = Field(None)


class BuildingUpdate(BaseModel):
    """Schema for updating a building."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    manager_id: Optional[str] = Field(None)


class BuildingResponse(BaseModel):
    """Schema for building response."""
    id: str
    name: str
    address: str
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BuildingListResponse(BaseModel):
    """Schema for paginated building list."""
    items: list[BuildingResponse]
    total: int
    skip: int
    limit: int
