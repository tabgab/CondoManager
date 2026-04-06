"""WebSocket connection manager for real-time notifications."""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""
    
    def __init__(self):
        """Initialize connection manager."""
        # Store active connections by user_id: {user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        settings = get_settings()
        self.heartbeat_interval = settings.WS_HEARTBEAT_INTERVAL
    
    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Accept WebSocket connection and store it.
        
        Args:
            websocket: The WebSocket connection object
            user_id: Unique identifier for the user
        """
        await websocket.accept()
        async with self._lock:
            # Disconnect existing connection for this user if any
            if user_id in self.active_connections:
                old_ws = self.active_connections[user_id]
                try:
                    await old_ws.close()
                except Exception:
                    pass
            self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user {user_id}")
    
    async def disconnect(self, user_id: str) -> None:
        """
        Remove WebSocket connection for a user.
        
        Args:
            user_id: User ID to disconnect
        """
        async with self._lock:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str) -> bool:
        """
        Send a message to a specific connected user.
        
        Args:
            message: Message data to send
            user_id: Target user ID
            
        Returns:
            True if message was sent, False if user not connected
        """
        websocket = None
        async with self._lock:
            websocket = self.active_connections.get(user_id)
        
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.warning(f"Failed to send message to {user_id}: {e}")
                # Remove broken connection
                await self.disconnect(user_id)
        return False
    
    async def broadcast(self, message: dict, role: Optional[str] = None) -> int:
        """
        Broadcast message to all connected users or users with specific role.
        
        Args:
            message: Message data to broadcast
            role: Optional role filter (sends to all if None)
            
        Returns:
            Number of users the message was sent to
        """
        sent_count = 0
        disconnected = []
        
        # Get copy of connections to avoid lock during send
        connections_copy = {}
        async with self._lock:
            connections_copy = self.active_connections.copy()
        
        for user_id, websocket in connections_copy.items():
            try:
                # TODO: Check user role if role filter provided
                # For now, send to all
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to broadcast to {user_id}: {e}")
                disconnected.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected:
            await self.disconnect(user_id)
        
        return sent_count
    
    def get_active_connections(self) -> List[str]:
        """
        Get list of currently connected user IDs.
        
        Returns:
            List of user IDs with active connections
        """
        return list(self.active_connections.keys())
    
    def is_connected(self, user_id: str) -> bool:
        """
        Check if a user is currently connected.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is connected
        """
        return user_id in self.active_connections
    
    async def close_all(self) -> None:
        """Close all active connections (for shutdown)."""
        async with self._lock:
            for user_id, websocket in self.active_connections.items():
                try:
                    await websocket.close()
                except Exception:
                    pass
            self.active_connections.clear()
        logger.info("All WebSocket connections closed")


# Global connection manager instance
manager = ConnectionManager()


async def handle_websocket_connection(
    websocket: WebSocket,
    user_id: str,
    user_email: str,
    user_role: str,
) -> None:
    """
    Handle WebSocket connection lifecycle.
    
    Args:
        websocket: The WebSocket connection
        user_id: User ID from JWT token
        user_email: User email from JWT token
        user_role: User role from JWT token
    """
    await manager.connect(websocket, user_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "WebSocket connection established",
        })
        
        # Handle incoming messages
        while True:
            try:
                # Receive message with timeout for heartbeat
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=manager.heartbeat_interval
                )
                
                # Handle different message types
                msg_type = data.get("type")
                
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "subscribe":
                    channels = data.get("channels", [])
                    await websocket.send_json({
                        "type": "subscribed",
                        "channels": channels,
                    })
                
                elif msg_type == "ack":
                    # Acknowledge notification receipt
                    notification_id = data.get("notification_id")
                    logger.debug(f"Notification {notification_id} acknowledged by {user_id}")
                
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    })
                    
            except asyncio.TimeoutError:
                # Send heartbeat ping
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await manager.disconnect(user_id)
