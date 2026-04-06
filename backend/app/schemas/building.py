"""Building Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BuildingCreate(BaseModel):
    """Schema for creating a building."""
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=300)
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Hungary", max_length=100)
    description: Optional[str] = Field(None)


class BuildingUpdate(BaseModel):
    """Schema for updating a building."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1, max_length=300)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)


class BuildingResponse(BaseModel):
    """Schema for building response."""
    id: str
    name: str
    address: str
    city: str
    postal_code: Optional[str] = None
    country: str
    description: Optional[str] = None
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
