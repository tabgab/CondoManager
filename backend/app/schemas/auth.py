"""Authentication and user schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class TokenRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Token response with access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserCreate(BaseModel):
    """User creation schema (for registration)."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(..., pattern="^(super_admin|manager|employee|owner|tenant)$")


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    
    model_config = {
        "from_attributes": True
    }


class UserLoginResponse(BaseModel):
    """Response for successful login including user info and tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
