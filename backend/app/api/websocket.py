"""WebSocket endpoint for real-time notifications."""
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.exceptions import HTTPException

from app.services.websocket import manager, handle_websocket_connection
from app.core.jwt import verify_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_user_from_ws_token(token: Optional[str] = Query(None)):
    """
    Extract and verify JWT token from WebSocket query parameter.
    
    Args:
        token: JWT token from query parameter
        
    Returns:
        dict with user_id, email, role
        
    Raises:
        HTTPException: if token is missing or invalid
    """
    if not token:
        raise HTTPException(status_code=401, detail="WebSocket connection requires authentication token")
    
    try:
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        return {
            "user_id": payload.get("user_id") or payload.get("sub"),
            "email": payload.get("sub"),
            "role": payload.get("role", "user"),
        }
    except Exception as e:
        logger.warning(f"WebSocket token validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
) -> None:
    """
    WebSocket endpoint for real-time notifications.
    
    Connection:
        - Connect with: ws://host/ws/notifications?token=JWT_TOKEN
        - Receives: {"type": "connected", "user_id": "..."}
    
    Messages:
        - Client sends: {"type": "ping"} -> Server responds: {"type": "pong"}
        - Client sends: {"type": "subscribe", "channels": ["tasks", "reports"]} -> Server responds: {"type": "subscribed"}
        - Client sends: {"type": "ack", "notification_id": "..."}
    
    Notifications:
        - Server sends: {"type": "notification", "payload": {...}}
    
    Args:
        websocket: FastAPI WebSocket object
        token: JWT authentication token from query parameter
    """
    # Authenticate the connection
    try:
        user = await get_current_user_from_ws_token(token)
    except HTTPException:
        await websocket.close(code=4001, reason="Authentication required")
        return
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    user_id = user["user_id"]
    user_email = user["email"]
    user_role = user["role"]
    
    logger.info(f"WebSocket connection attempt from user {user_id} ({user_email})")
    
    try:
        await handle_websocket_connection(
            websocket=websocket,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
        )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
