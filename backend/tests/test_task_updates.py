"""Task update endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

os.environ["SECRET_KEY"] = "test-secret-key-for-task-update-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.core.jwt import create_access_token
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_update import TaskUpdate


def create_auth_token(email: str, role: str) -> str:
    token_data = {"sub": email, "role": role}
    return create_access_token(token_data)


@pytest_asyncio.fixture(scope="function")
async def test_setup():
    """Create fresh engine and tables for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine, TestingSessionLocal
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_setup):
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def manager_user(test_setup):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        user = User(
            email="manager@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Manager",
            last_name="User",
            role=UserRole.MANAGER,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def employee_user(test_setup):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        user = User(
            email="employee@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Employee",
            last_name="User",
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def sample_building(test_setup):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        building = Building(
            name="Test Building",
            address="123 Test Street",
            city="Budapest",
            postal_code="1000",
            country="Hungary",
        )
        session.add(building)
        await session.commit()
        await session.refresh(building)
        return building


@pytest_asyncio.fixture
async def sample_task(test_setup, manager_user, employee_user, sample_building):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        task = Task(
            title="Sample Task",
            description="A sample task for testing",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            created_by_id=manager_user.id,
            assignee_id=employee_user.id,
            building_id=sample_building.id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


class TestListTaskUpdates:
    """Test GET /tasks/{task_id}/updates endpoint."""

    @pytest.mark.asyncio
    async def test_list_updates_as_manager(self, client, manager_user, sample_task):
        """Manager can list updates for any task."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_updates_as_assigned_employee(self, client, employee_user, sample_task):
        """Assigned employee can list updates for their task."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_list_updates_unauthorized_returns_401(self, client, sample_task):
        """Unauthenticated user cannot list task updates."""
        response = await client.get(f"/tasks/{sample_task.id}/updates")
        
        assert response.status_code == 401


class TestCreateTaskUpdate:
    """Test POST /tasks/{task_id}/updates endpoint."""

    @pytest.mark.asyncio
    async def test_add_progress_update_as_employee(self, client, employee_user, sample_task):
        """Assigned employee can add progress updates."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {
            "content": "Started working on the pipe",
            "percentage_complete": 25,
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Started working on the pipe"
        assert data["percentage_complete"] == 25
        assert data["author_id"] == employee_user.id

    @pytest.mark.asyncio
    async def test_add_concern_requiring_manager_attention(self, client, employee_user, sample_task):
        """Employee can flag concern requiring manager attention."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {
            "content": "Need specialized tools not available",
            "is_concern": True,
            "requires_manager_attention": True,
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_concern"] is True
        assert data["requires_manager_attention"] is True

    @pytest.mark.asyncio
    async def test_manager_can_add_updates(self, client, manager_user, sample_task):
        """Manager can add updates to any task."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {
            "content": "Reviewing progress",
            "percentage_complete": 50,
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Reviewing progress"

    @pytest.mark.asyncio
    async def test_unauthorized_user_cannot_add_updates(self, client, sample_task):
        """Unauthenticated user cannot add task updates."""
        update_data = {
            "content": "Unauthorized update",
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            json=update_data,
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_task_id_returns_404(self, client, manager_user):
        """Adding update to non-existent task returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {
            "content": "Test update",
        }
        
        response = await client.post(
            "/tasks/invalid-id/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 404


class TestTaskUpdateContent:
    """Test update content validation."""

    @pytest.mark.asyncio
    async def test_update_requires_content(self, client, employee_user, sample_task):
        """Update must have content."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {
            # Missing content
            "percentage_complete": 50,
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_percentage_complete_bounds(self, client, employee_user, sample_task):
        """Percentage complete must be between 0 and 100."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {
            "content": "Progress update",
            "percentage_complete": 150,  # Invalid: > 100
        }
        
        response = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 422


class TestTaskUpdateTracking:
    """Test progress tracking functionality."""

    @pytest.mark.asyncio
    async def test_percentage_complete_tracking(self, client, test_setup, employee_user, sample_task):
        """Multiple updates track progress over time."""
        engine, TestingSessionLocal = test_setup
        token = create_auth_token("employee@example.com", "employee")
        
        # First update: 25%
        response1 = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Started", "percentage_complete": 25},
        )
        assert response1.status_code == 201
        
        # Second update: 50%
        response2 = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Halfway", "percentage_complete": 50},
        )
        assert response2.status_code == 201
        
        # Third update: 75%
        response3 = await client.post(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Almost done", "percentage_complete": 75},
        )
        assert response3.status_code == 201
        
        # List updates and verify all are present
        response = await client.get(
            f"/tasks/{sample_task.id}/updates",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        percentages = [item["percentage_complete"] for item in data["items"]]
        assert 25 in percentages
        assert 50 in percentages
        assert 75 in percentages
