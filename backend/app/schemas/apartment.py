"""Apartment Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ApartmentCreate(BaseModel):
    """Schema for creating an apartment."""
    building_id: str
    unit_number: str = Field(..., min_length=1, max_length=50)
    floor: Optional[int] = Field(None)
    owner_id: Optional[str] = Field(None)
    tenant_id: Optional[str] = Field(None)
    description: Optional[str] = Field(None)


class ApartmentUpdate(BaseModel):
    """Schema for updating an apartment."""
    unit_number: Optional[str] = Field(None, min_length=1, max_length=50)
    floor: Optional[int] = Field(None)
    owner_id: Optional[str] = Field(None)
    tenant_id: Optional[str] = Field(None)
    description: Optional[str] = Field(None)


class UserInfo(BaseModel):
    """Minimal user info for apartment response."""
    id: str
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class ApartmentUserCreate(BaseModel):
    """Schema for assigning a user to an apartment."""
    user_id: str
    role: str = Field(..., pattern='^(owner|tenant)$')  # 'owner' or 'tenant'


class ApartmentUserResponse(BaseModel):
    """Schema for apartment-user association response."""
    id: str
    user_id: str
    role: str
    user: Optional[UserInfo] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApartmentResponse(BaseModel):
    """Schema for apartment response."""
    id: str
    building_id: str
    unit_number: str
    floor: Optional[int] = None
    owner_id: Optional[str] = None
    tenant_id: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[UserInfo] = None
    tenant: Optional[UserInfo] = None
    users: list[ApartmentUserResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApartmentListResponse(BaseModel):
    """Schema for paginated apartment list."""
    items: list[ApartmentResponse]
    total: int
    skip: int
    limit: int
