"""Push subscription schemas for Web Push notifications."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class PushSubscriptionCreate(BaseModel):
    """Schema for creating a push subscription."""
    endpoint: str = Field(..., min_length=10, max_length=500, description="Browser push endpoint URL")
    p256dh: str = Field(..., min_length=10, max_length=255, description="P256DH public key")
    auth: str = Field(..., min_length=10, max_length=255, description="Auth key")
    device_info: Optional[str] = Field(None, max_length=255, description="Device/browser information")


class PushSubscriptionResponse(BaseModel):
    """Schema for push subscription response."""
    id: str
    endpoint: str
    device_info: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PushSubscriptionListResponse(BaseModel):
    """Schema for list of push subscriptions."""
    items: List[PushSubscriptionResponse]
    total: int


class PushNotificationPayload(BaseModel):
    """Schema for push notification payload sent to browser."""
    title: str = Field(..., min_length=1, max_length=100, description="Notification title")
    body: str = Field(..., min_length=1, max_length=200, description="Notification body")
    icon: Optional[str] = Field("/icon-192x192.png", description="Notification icon URL")
    badge: Optional[str] = Field("/badge-72x72.png", description="Notification badge URL")
    image: Optional[str] = Field(None, description="Notification image URL")
    tag: Optional[str] = Field(None, description="Notification tag for grouping")
    require_interaction: bool = Field(False, description="Whether notification requires user interaction")
    data: Optional[Dict[str, Any]] = Field(None, description="Custom data payload")
    actions: Optional[List[Dict[str, str]]] = Field(None, description="Notification actions")
    url: Optional[str] = Field(None, description="URL to open on click")


class UnsubscribeRequest(BaseModel):
    """Schema for unsubscribe request by endpoint."""
    endpoint: str = Field(..., min_length=10, description="Endpoint URL to unsubscribe")


class VapidPublicKeyResponse(BaseModel):
    """Schema for VAPID public key response."""
    public_key: str = Field(..., description="VAPID public key for browser subscription")
