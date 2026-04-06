"""WebSocket notification tests - TDD approach."""
import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.services.websocket import ConnectionManager
from app.core.jwt import create_access_token


class TestConnectionManager:
    """Test ConnectionManager class."""

    def test_init_connection_manager(self):
        """ConnectionManager initializes correctly."""
        manager = ConnectionManager()
        assert isinstance(manager.active_connections, dict)
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_connect_stores_connection(self):
        """Connect stores websocket by user_id."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()

        await manager.connect(mock_websocket, "user-123")

        assert "user-123" in manager.active_connections
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self):
        """Disconnect removes websocket for user_id."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        await manager.connect(mock_websocket, "user-123")

        await manager.disconnect("user-123")

        assert "user-123" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """Send message to specific connected user."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        await manager.connect(mock_websocket, "user-123")

        message = {"type": "notification", "title": "Test"}
        await manager.send_personal_message(message, "user-123")

        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_personal_message_user_not_connected(self):
        """Sending to disconnected user does nothing."""
        manager = ConnectionManager()

        message = {"type": "notification", "title": "Test"}
        # Should not raise
        await manager.send_personal_message(message, "nonexistent-user")

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all(self):
        """Broadcast sends message to all connected users."""
        manager = ConnectionManager()

        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await manager.connect(ws1, "user-1")
        await manager.connect(ws2, "user-2")

        message = {"type": "broadcast", "data": "hello"}
        await manager.broadcast(message)

        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_get_active_connections(self):
        """Get list of connected user IDs."""
        manager = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.connect(ws1, "user-1")
        await manager.connect(ws2, "user-2")

        connections = manager.get_active_connections()

        assert len(connections) == 2
        assert "user-1" in connections
        assert "user-2" in connections


class TestWebSocketEndpoint:
    """Test WebSocket endpoint integration."""

    @pytest.mark.asyncio
    async def test_websocket_connection_with_valid_token(self):
        """WebSocket connects with valid JWT token."""
        from httpx import AsyncClient, ASGITransport

        from app.main import app
        from app.services.websocket import manager

        token = create_access_token({"sub": "user@test.com", "role": "manager", "user_id": "user-123"})

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # WebSocket test via main app
            from fastapi.testclient import TestClient

            # Use test client for WebSocket
            with TestClient(app) as client_sync:
                with client_sync.websocket_connect(f"/ws/notifications?token={token}") as ws:
                    # Receive connected message
                    data = ws.receive_json()
                    assert data["type"] == "connected"
                    assert data["user_id"] == "user-123"

        # Cleanup
        await manager.disconnect("user-123")

    @pytest.mark.asyncio
    async def test_websocket_without_token_rejected(self):
        """WebSocket without token is rejected."""
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            with pytest.raises(Exception):
                with client.websocket_connect("/ws/notifications"):
                    pass

    @pytest.mark.asyncio
    async def test_websocket_invalid_token_rejected(self):
        """WebSocket with invalid token is rejected."""
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            with pytest.raises(Exception):
                with client.websocket_connect("/ws/notifications?token=invalid-token"):
                    pass

    @pytest.mark.asyncio
    async def test_websocket_heartbeat_ping_pong(self):
        """WebSocket responds to ping with pong."""
        from fastapi.testclient import TestClient
        from app.main import app

        token = create_access_token({"sub": "user@test.com", "role": "manager", "user_id": "user-123"})

        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/notifications?token={token}") as ws:
                # Skip connected message
                ws.receive_json()

                # Send ping
                ws.send_json({"type": "ping"})

                # Receive pong
                data = ws.receive_json()
                assert data["type"] == "pong"


class TestNotificationTypes:
    """Test notification schemas."""

    def test_notification_type_enum(self):
        """NotificationType enum has expected values."""
        from app.schemas.notification import NotificationType

        assert NotificationType.TASK_ASSIGNED == "task_assigned"
        assert NotificationType.TASK_UPDATED == "task_updated"
        assert NotificationType.REPORT_SUBMITTED == "report_submitted"
        assert NotificationType.REPORT_ACKNOWLEDGED == "report_acknowledged"

    def test_notification_payload_creation(self):
        """NotificationPayload can be created with all fields."""
        from app.schemas.notification import NotificationPayload, NotificationType
        from datetime import datetime

        payload = NotificationPayload(
            type=NotificationType.TASK_ASSIGNED,
            title="New Task",
            message="You have been assigned a new task",
            data={"task_id": "123", "building_id": "456"},
            timestamp=datetime.utcnow(),
        )

        assert payload.type == NotificationType.TASK_ASSIGNED
        assert payload.title == "New Task"
        assert "task_id" in payload.data
