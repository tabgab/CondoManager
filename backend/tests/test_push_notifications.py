"""Web Push notification tests - TDD approach."""
import os
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["VAPID_PUBLIC_KEY"] = "test-vapid-public-key"
os.environ["VAPID_PRIVATE_KEY"] = "test-vapid-private-key"
os.environ["VAPID_CLAIMS_SUB"] = "mailto:test@condomanager.app"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.core.jwt import create_access_token


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


def create_auth_token(email: str, role: str, user_id: str = None) -> str:
    token_data = {"sub": email, "role": role}
    if user_id:
        token_data["user_id"] = user_id
    return create_access_token(token_data)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def manager_user(test_db):
    async with TestingSessionLocal() as session:
        user = User(
            email="manager@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Manager",
            last_name="User",
            role="manager",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


class TestCreatePushSubscription:
    """Test POST /push-subscriptions endpoint."""

    @pytest.mark.asyncio
    async def test_create_subscription_as_authenticated_user(self, client, manager_user):
        """Authenticated user can create push subscription."""
        token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-device-token",
            "p256dh": "test-p256dh-key",
            "auth": "test-auth-key",
            "device_info": "Chrome on Windows",
        }
        
        response = await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json=subscription_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["endpoint"] == subscription_data["endpoint"]
        assert data["p256dh"] == subscription_data["p256dh"]
        assert data["auth"] == subscription_data["auth"]
        assert data["device_info"] == subscription_data["device_info"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_subscription_without_auth_returns_401(self, client):
        """Unauthenticated user cannot create subscription."""
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test",
            "p256dh": "test-key",
            "auth": "test-auth",
        }
        
        response = await client.post("/push-subscriptions", json=subscription_data)
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_duplicate_subscription_updates_existing(self, client, manager_user):
        """Creating subscription with same endpoint updates existing."""
        token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/test-device",
            "p256dh": "test-p256dh-key",
            "auth": "test-auth-key",
        }
        
        # Create first subscription
        response1 = await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json=subscription_data,
        )
        assert response1.status_code == 201
        first_id = response1.json()["id"]
        
        # Create second subscription with same endpoint
        subscription_data["auth"] = "new-auth-key"
        response2 = await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json=subscription_data,
        )
        
        assert response2.status_code == 201
        # Should update existing, not create new
        assert response2.json()["id"] == first_id
        assert response2.json()["auth"] == "new-auth-key"


class TestDeletePushSubscription:
    """Test DELETE /push-subscriptions/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_own_subscription(self, client, manager_user):
        """User can delete their own subscription."""
        token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        
        # Create subscription first
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/delete-test",
            "p256dh": "test-key",
            "auth": "test-auth",
        }
        create_response = await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json=subscription_data,
        )
        subscription_id = create_response.json()["id"]
        
        # Delete subscription
        response = await client.delete(
            f"/push-subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_other_user_subscription_returns_403(self, client, manager_user):
        """User cannot delete another user's subscription."""
        # Create another user
        async with TestingSessionLocal() as session:
            other_user = User(
                email="other@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Other",
                last_name="User",
                role="employee",
                is_active=True,
            )
            session.add(other_user)
            await session.commit()
            await session.refresh(other_user)
            other_user_id = other_user.id
        
        # Create subscription for other user
        other_token = create_auth_token("other@example.com", "employee", str(other_user_id))
        subscription_data = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/other-device",
            "p256dh": "test-key",
            "auth": "test-auth",
        }
        create_response = await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {other_token}"},
            json=subscription_data,
        )
        subscription_id = create_response.json()["id"]
        
        # Try to delete as manager
        manager_token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        response = await client.delete(
            f"/push-subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        
        assert response.status_code == 403


class TestPushNotificationService:
    """Test PushNotificationService."""

    def test_service_initialization(self):
        """Service initializes with VAPID keys."""
        from app.services.push_notification import PushNotificationService
        
        service = PushNotificationService()
        assert service.vapid_public_key == "test-vapid-public-key"
        assert service.vapid_private_key == "test-vapid-private-key"

    @pytest.mark.asyncio
    async def test_send_notification_success(self):
        """Send notification to single subscription."""
        from app.services.push_notification import PushNotificationService
        
        with patch("app.services.push_notification.webpush") as mock_webpush:
            mock_webpush.return_value = Mock(status_code=201)
            
            service = PushNotificationService()
            subscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test",
                "p256dh": "test-p256dh",
                "auth": "test-auth",
            }
            
            result = await service.send_notification(
                subscription=subscription,
                title="Test Title",
                body="Test Body",
            )
            
            assert result is True
            mock_webpush.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_invalid_subscription(self):
        """Invalid subscription should be marked for deletion."""
        from app.services.push_notification import PushNotificationService, WebPushException
        
        with patch("app.services.push_notification.webpush") as mock_webpush:
            mock_webpush.side_effect = WebPushException("Invalid subscription")
            
            service = PushNotificationService()
            subscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/invalid",
                "p256dh": "test-p256dh",
                "auth": "test-auth",
            }
            
            result = await service.send_notification(
                subscription=subscription,
                title="Test",
                body="Test",
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_send_to_user_with_multiple_devices(self):
        """Send notification to all user's devices."""
        from app.services.push_notification import PushNotificationService
        
        with patch.object(PushNotificationService, "send_notification") as mock_send:
            mock_send.return_value = True
            
            service = PushNotificationService()
            service._subscriptions_cache = {
                "user-123": [
                    {"endpoint": "device-1", "p256dh": "key1", "auth": "auth1"},
                    {"endpoint": "device-2", "p256dh": "key2", "auth": "auth2"},
                ]
            }
            
            result = await service.send_to_user(
                user_id="user-123",
                title="Test",
                body="Test",
            )
            
            assert result == 2  # Sent to 2 devices
            assert mock_send.call_count == 2


class TestUnsubscribeByEndpoint:
    """Test POST /push-subscriptions/unsubscribe endpoint."""

    @pytest.mark.asyncio
    async def test_unsubscribe_by_endpoint(self, client, manager_user):
        """Unsubscribe using endpoint URL."""
        token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        endpoint = "https://fcm.googleapis.com/fcm/send/unsubscribe-test"
        
        # Create subscription first
        await client.post(
            "/push-subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "endpoint": endpoint,
                "p256dh": "test-key",
                "auth": "test-auth",
            },
        )
        
        # Unsubscribe by endpoint
        response = await client.post(
            "/push-subscriptions/unsubscribe",
            headers={"Authorization": f"Bearer {token}"},
            json={"endpoint": endpoint},
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_endpoint(self, client, manager_user):
        """Unsubscribe nonexistent endpoint returns 404."""
        token = create_auth_token("manager@example.com", "manager", str(manager_user.id))
        
        response = await client.post(
            "/push-subscriptions/unsubscribe",
            headers={"Authorization": f"Bearer {token}"},
            json={"endpoint": "https://nonexistent.endpoint.com"},
        )
        
        assert response.status_code == 404
