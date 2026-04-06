"""User schemas for updates and list responses."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import UserResponse


class UserUpdate(BaseModel):
    """User update schema - partial updates allowed."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(super_admin|manager|employee|owner|tenant)$")
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    """Paginated list response for users."""
    items: List[UserResponse]
    total: int
    skip: int
    limit: int
