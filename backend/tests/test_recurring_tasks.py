"""Recurring task endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

os.environ["SECRET_KEY"] = "test-secret-key-for-recurring-tasks"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.core.jwt import create_access_token
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.recurring_task import RecurringTask, RecurringFrequency


def create_auth_token(email: str, role: str) -> str:
    token_data = {"sub": email, "role": role}
    return create_access_token(token_data)


@pytest_asyncio.fixture(scope="function")
async def test_setup():
    """Create fresh engine and tables for each test."""
    import tempfile
    import os
    
    # Use file-based SQLite for proper session sharing across HTTP requests
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
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
    os.unlink(db_path)


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
async def sample_recurring_task(test_setup, manager_user, employee_user, sample_building):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        recurring = RecurringTask(
            template_title="Weekly Cleaning",
            template_description="Clean common areas",
            frequency=RecurringFrequency.WEEKLY,
            day_of_week=1,  # Monday
            hour=9,
            assignee_id=employee_user.id,
            building_id=sample_building.id,
            created_by_id=manager_user.id,
            is_active=True,
        )
        session.add(recurring)
        await session.commit()
        await session.refresh(recurring)
        return recurring


class TestListRecurringTasks:
    """Test GET /recurring-tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_as_manager(self, client, manager_user, sample_recurring_task):
        """Manager can list all recurring tasks."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/recurring-tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert data["items"][0]["template_title"] == "Weekly Cleaning"

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_as_employee_returns_403(self, client, employee_user, sample_recurring_task):
        """Employee cannot list recurring tasks."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            "/recurring-tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_recurring_tasks_without_auth_returns_401(self, client):
        """Unauthenticated user cannot list recurring tasks."""
        response = await client.get("/recurring-tasks")
        
        assert response.status_code == 401


class TestCreateRecurringTask:
    """Test POST /recurring-tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_recurring_task_as_manager_returns_201(self, client, manager_user, employee_user, sample_building):
        """Manager can create a recurring task template."""
        token = create_auth_token("manager@example.com", "manager")
        recurring_data = {
            "template_title": "Monthly Inspection",
            "template_description": "Inspect fire safety equipment",
            "frequency": "monthly",
            "day_of_month": 15,
            "hour": 10,
            "assignee_id": str(employee_user.id),
            "building_id": str(sample_building.id),
        }
        
        response = await client.post(
            "/recurring-tasks",
            headers={"Authorization": f"Bearer {token}"},
            json=recurring_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["template_title"] == "Monthly Inspection"
        assert data["frequency"] == "monthly"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_recurring_task_as_employee_returns_403(self, client, employee_user, sample_building):
        """Employee cannot create recurring tasks."""
        token = create_auth_token("employee@example.com", "employee")
        recurring_data = {
            "template_title": "Unauthorized",
            "template_description": "Should not be created",
            "frequency": "daily",
            "hour": 8,
            "building_id": str(sample_building.id),
        }
        
        response = await client.post(
            "/recurring-tasks",
            headers={"Authorization": f"Bearer {token}"},
            json=recurring_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_recurring_task_without_auth_returns_401(self, client, sample_building):
        """Unauthenticated user cannot create recurring tasks."""
        recurring_data = {
            "template_title": "Anonymous",
            "template_description": "Should not be created",
            "frequency": "daily",
            "hour": 8,
            "building_id": str(sample_building.id),
        }
        
        response = await client.post(
            "/recurring-tasks",
            json=recurring_data,
        )
        
        assert response.status_code == 401


class TestGetRecurringTask:
    """Test GET /recurring-tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_recurring_task_as_manager(self, client, manager_user, sample_recurring_task):
        """Manager can get any recurring task."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/recurring-tasks/{sample_recurring_task.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_recurring_task.id)
        assert data["template_title"] == "Weekly Cleaning"

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_nonexistent_recurring_task_returns_404(self, client, manager_user):
        """Getting non-existent recurring task returns 404."""
        from uuid import uuid4
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/recurring-tasks/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestUpdateRecurringTask:
    """Test PATCH /recurring-tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_recurring_task_as_manager(self, client, manager_user, sample_recurring_task):
        """Manager can update a recurring task."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {
            "template_title": "Updated Title",
            "frequency": "daily",
            "hour": 14,
        }
        
        response = await client.patch(
            f"/recurring-tasks/{sample_recurring_task.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["template_title"] == "Updated Title"
        assert data["frequency"] == "daily"
        assert data["hour"] == 14

    @pytest.mark.asyncio
    async def test_update_recurring_task_as_employee_returns_403(self, client, employee_user, sample_recurring_task):
        """Employee cannot update recurring tasks."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {"template_title": "Hacked"}
        
        response = await client.patch(
            f"/recurring-tasks/{sample_recurring_task.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 403


class TestDeleteRecurringTask:
    """Test DELETE /recurring-tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_recurring_task_as_manager(self, client, test_setup, manager_user, employee_user, sample_building):
        """Manager can delete a recurring task."""
        engine, TestingSessionLocal = test_setup
        # Create a recurring task to delete
        async with TestingSessionLocal() as session:
            recurring = RecurringTask(
                template_title="To Delete",
                template_description="Will be deleted",
                frequency=RecurringFrequency.DAILY,
                hour=8,
                assignee_id=employee_user.id,
                building_id=sample_building.id,
                created_by_id=manager_user.id,
                is_active=True,
            )
            session.add(recurring)
            await session.commit()
            await session.refresh(recurring)
            recurring_id = recurring.id
        
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            f"/recurring-tasks/{recurring_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_recurring_task_as_employee_returns_403(self, client, employee_user, sample_recurring_task):
        """Employee cannot delete recurring tasks."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.delete(
            f"/recurring-tasks/{sample_recurring_task.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_recurring_task_returns_404(self, client, manager_user):
        """Deleting non-existent recurring task returns 404."""
        from uuid import uuid4
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            f"/recurring-tasks/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestToggleRecurringTask:
    """Test PATCH /recurring-tasks/{id}/toggle endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_recurring_task_inactive(self, client, manager_user, sample_recurring_task):
        """Manager can toggle recurring task inactive."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.patch(
            f"/recurring-tasks/{sample_recurring_task.id}/toggle",
            headers={"Authorization": f"Bearer {token}"},
            json={"is_active": False},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_toggle_recurring_task_active(self, client, test_setup, manager_user, employee_user, sample_building):
        """Manager can toggle recurring task active."""
        engine, TestingSessionLocal = test_setup
        # Create inactive recurring task
        async with TestingSessionLocal() as session:
            recurring = RecurringTask(
                template_title="Inactive Task",
                template_description="Currently inactive",
                frequency=RecurringFrequency.WEEKLY,
                day_of_week=3,
                hour=10,
                assignee_id=employee_user.id,
                building_id=sample_building.id,
                created_by_id=manager_user.id,
                is_active=False,
            )
            session.add(recurring)
            await session.commit()
            await session.refresh(recurring)
            recurring_id = recurring.id
        
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.patch(
            f"/recurring-tasks/{recurring_id}/toggle",
            headers={"Authorization": f"Bearer {token}"},
            json={"is_active": True},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_toggle_recurring_task_as_employee_returns_403(self, client, employee_user, sample_recurring_task):
        """Employee cannot toggle recurring tasks."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.patch(
            f"/recurring-tasks/{sample_recurring_task.id}/toggle",
            headers={"Authorization": f"Bearer {token}"},
            json={"is_active": False},
        )
        
        assert response.status_code == 403
