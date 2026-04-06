"""User management endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key-for-user-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.core.jwt import create_access_token


# Override database dependency with in-memory SQLite
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Dependency override for testing."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


def create_auth_token(email: str, role: str) -> str:
    """Helper to create a valid auth token."""
    token_data = {"sub": email, "role": role}
    return create_access_token(token_data)


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
async def manager_user(test_db):
    """Create a manager user."""
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


@pytest_asyncio.fixture
async def employee_user(test_db):
    """Create an employee user."""
    async with TestingSessionLocal() as session:
        user = User(
            email="employee@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Employee",
            last_name="User",
            role="employee",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def owner_user(test_db):
    """Create an owner user."""
    async with TestingSessionLocal() as session:
        user = User(
            email="owner@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Owner",
            last_name="User",
            role="owner",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def multiple_users(test_db):
    """Create multiple users for listing tests."""
    async with TestingSessionLocal() as session:
        users = [
            User(email=f"user{i}@example.com", hashed_password=get_password_hash("pass"), first_name=f"User{i}", last_name="Test", role="owner", is_active=True)
            for i in range(5)
        ]
        session.add_all(users)
        await session.commit()
        return users


class TestListUsers:
    """Test GET /users endpoint with RBAC."""

    @pytest.mark.asyncio
    async def test_list_users_as_manager_returns_200(self, client, manager_user, multiple_users):
        """Manager can list all users."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 6  # manager + 5 test users

    @pytest.mark.asyncio
    async def test_list_users_as_employee_returns_403(self, client, employee_user):
        """Employee cannot list all users."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            "/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, client, manager_user, multiple_users):
        """Test pagination with skip and limit."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/users?skip=0&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 3

    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(self, client, manager_user, employee_user, owner_user):
        """Filter users by role."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/users?role=owner",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        for user in data["items"]:
            assert user["role"] == "owner"

    @pytest.mark.asyncio
    async def test_list_users_without_auth_returns_401(self, client):
        """Unauthenticated user cannot list users."""
        response = await client.get("/users")
        
        assert response.status_code == 401


class TestGetUser:
    """Test GET /users/{user_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_manager(self, client, manager_user, owner_user):
        """Manager can get any user by ID."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "owner@example.com"
        assert data["id"] == owner_user.id

    @pytest.mark.asyncio
    async def test_get_own_profile(self, client, owner_user):
        """User can get their own profile."""
        token = create_auth_token("owner@example.com", "owner")
        response = await client.get(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "owner@example.com"

    @pytest.mark.asyncio
    async def test_get_other_user_as_owner_returns_403(self, client, owner_user, employee_user):
        """Owner cannot get another user's profile."""
        token = create_auth_token("owner@example.com", "owner")
        response = await client.get(
            f"/users/{employee_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_returns_404(self, client, manager_user):
        """Getting non-existent user returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/users/nonexistent-id-12345",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestUpdateUser:
    """Test PATCH /users/{user_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_own_profile(self, client, owner_user):
        """User can update their own profile."""
        token = create_auth_token("owner@example.com", "owner")
        update_data = {"first_name": "Updated", "phone": "+1234567890"}
        
        response = await client.patch(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["phone"] == "+1234567890"

    @pytest.mark.asyncio
    async def test_manager_can_update_any_user(self, client, manager_user, owner_user):
        """Manager can update any user's profile."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {"first_name": "ManagerUpdated", "role": "tenant"}
        
        response = await client.patch(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "ManagerUpdated"

    @pytest.mark.asyncio
    async def test_owner_cannot_update_another_user(self, client, owner_user, employee_user):
        """Owner cannot update another user's profile."""
        token = create_auth_token("owner@example.com", "owner")
        update_data = {"first_name": "Hacked"}
        
        response = await client.patch(
            f"/users/{employee_user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_user_returns_404(self, client, manager_user):
        """Updating non-existent user returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.patch(
            "/users/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Test"},
        )
        
        assert response.status_code == 404


class TestDeleteUser:
    """Test DELETE /users/{user_id} endpoint (soft delete)."""

    @pytest.mark.asyncio
    async def test_manager_can_delete_user(self, client, manager_user, owner_user):
        """Manager can soft delete any user."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["id"] == owner_user.id

    @pytest.mark.asyncio
    async def test_employee_cannot_delete_user(self, client, employee_user, owner_user):
        """Employee cannot delete users."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.delete(
            f"/users/{owner_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_owner_cannot_delete_other_user(self, client, owner_user, employee_user):
        """Owner cannot delete another user."""
        token = create_auth_token("owner@example.com", "owner")
        
        response = await client.delete(
            f"/users/{employee_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user_returns_404(self, client, manager_user):
        """Deleting non-existent user returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            "/users/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestUnauthorizedAccess:
    """Test unauthorized access returns proper errors."""

    @pytest.mark.asyncio
    async def test_access_without_token_returns_401(self, client, owner_user):
        """Accessing protected endpoint without token returns 401."""
        response = await client.get(f"/users/{owner_user.id}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_with_invalid_token_returns_401(self, client, owner_user):
        """Accessing with invalid token returns 401."""
        response = await client.get(
            f"/users/{owner_user.id}",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        
        assert response.status_code == 401
