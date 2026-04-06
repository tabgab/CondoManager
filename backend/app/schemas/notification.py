"""Notification schemas for WebSocket messages."""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Types of notifications sent via WebSocket."""
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_VERIFIED = "task_verified"
    REPORT_SUBMITTED = "report_submitted"
    REPORT_ACKNOWLEDGED = "report_acknowledged"
    REPORT_REJECTED = "report_rejected"
    MESSAGE_RECEIVED = "message_received"
    SYSTEM = "system"


class NotificationPayload(BaseModel):
    """Payload for a notification message."""
    type: NotificationType = Field(..., description="Type of notification")
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WebSocketMessage(BaseModel):
    """Generic WebSocket message format."""
    type: str = Field(..., description="Message type: notification, ping, pong, connected")
    payload: Optional[NotificationPayload] = None
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class ConnectionResponse(BaseModel):
    """Response sent on successful WebSocket connection."""
    type: str = "connected"
    user_id: str
    message: str = "WebSocket connection established"
