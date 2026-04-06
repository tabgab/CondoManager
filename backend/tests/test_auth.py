"""Authentication endpoint tests - TDD approach."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from jose import jwt

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key-for-auth-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User


# Override database dependency with in-memory SQLite
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Dependency override for testing."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database and tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_db):
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(test_db):
    """Create a test user in database."""
    async with TestingSessionLocal() as session:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123"),
            first_name="Test",
            last_name="User",
            role="owner",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


class TestLogin:
    """Test suite for login endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, client, test_user):
        """Test successful login returns access and refresh tokens."""
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check token response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        
        # Verify user info
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["role"] == "owner"
        
        # Verify tokens are valid JWTs
        assert data["access_token"].count(".") == 2
        assert data["refresh_token"].count(".") == 2

    @pytest.mark.asyncio
    async def test_login_with_invalid_password_returns_401(self, client, test_user):
        """Test login with wrong password returns 401."""
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email_returns_401(self, client):
        """Test login with non-existent email returns 401."""
        response = await client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user_returns_401(self, client, test_db):
        """Test login with inactive user returns 401."""
        async with TestingSessionLocal() as session:
            user = User(
                email="inactive@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Inactive",
                last_name="User",
                role="owner",
                is_active=False,
            )
            session.add(user)
            await session.commit()
        
        response = await client.post(
            "/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        
        assert response.status_code == 401


class TestRefreshToken:
    """Test suite for refresh token endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_returns_new_access_token(self, client, test_user):
        """Test refresh endpoint returns new access token."""
        # First login to get refresh token
        login_response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["access_token"].count(".") == 2

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token_returns_401(self, client):
        """Test refresh with invalid token returns 401."""
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        
        assert response.status_code == 401


class TestProtectedAccess:
    """Test accessing protected endpoints with tokens."""

    @pytest.mark.asyncio
    async def test_access_protected_with_valid_token(self, client, test_user):
        """Test accessing protected endpoint with valid access token."""
        # Login to get token
        login_response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        
        # Access protected endpoint (me endpoint)
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_access_protected_without_token_returns_401(self, client):
        """Test accessing protected endpoint without token returns 401."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_with_invalid_token_returns_401(self, client):
        """Test accessing protected endpoint with invalid token returns 401."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        
        assert response.status_code == 401


class TestRegister:
    """Test suite for user registration."""

    @pytest.mark.asyncio
    async def test_register_new_user(self, client, test_db):
        """Test registering a new user."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone": "+1234567890",
            "role": "tenant",
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["role"] == "tenant"
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_409(self, client, test_user):
        """Test registering with existing email returns 409."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Another",
            "last_name": "User",
            "role": "owner",
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
