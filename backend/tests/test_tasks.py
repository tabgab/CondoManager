"""Task endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

os.environ["SECRET_KEY"] = "test-secret-key-for-task-endpoint-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.core.jwt import create_access_token
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.apartment import Apartment
from app.models.task import Task, TaskStatus, TaskPriority


def create_auth_token(email: str, role: str) -> str:
    token_data = {"sub": email, "role": role}
    return create_access_token(token_data)


@pytest_asyncio.fixture(scope="function")
async def test_setup():
    """Create fresh engine and tables for each test."""
    # Create fresh in-memory database for each test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Override the dependency
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine, TestingSessionLocal
    
    # Cleanup
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
            role="manager",
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
            role="employee",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def building(test_setup):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        building = Building(
            name="Test Building",
            address="123 Test St",
            city="Test City",
            postal_code="12345",
            country="Test Country",
        )
        session.add(building)
        await session.commit()
        await session.refresh(building)
        return building


@pytest_asyncio.fixture
async def sample_task(test_setup, manager_user, employee_user, building):
    engine, TestingSessionLocal = test_setup
    async with TestingSessionLocal() as session:
        task = Task(
            title="Test Task",
            description="A test task description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.NORMAL,
            created_by_id=manager_user.id,
            assignee_id=employee_user.id,
            building_id=building.id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


class TestListTasks:
    """Test GET /tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_tasks_as_manager_sees_all(self, client, manager_user, employee_user, building, sample_task):
        """Manager can see all tasks."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_tasks_as_employee_sees_assigned_only(self, client, manager_user, employee_user, building, sample_task):
        """Employee only sees assigned tasks."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Employee should only see tasks assigned to them
        for item in data["items"]:
            assert item["assignee_id"] == str(employee_user.id)

    @pytest.mark.asyncio
    async def test_list_tasks_without_auth_returns_401(self, client):
        """Unauthenticated user cannot list tasks."""
        response = await client.get("/tasks")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, client, manager_user, sample_task):
        """Manager can filter tasks by status."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/tasks?status=pending",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        for item in data["items"]:
            assert item["status"] == "pending"


class TestCreateTask:
    """Test POST /tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_as_manager_returns_201(self, client, manager_user, employee_user, building):
        """Manager can create a task."""
        token = create_auth_token("manager@example.com", "manager")
        task_data = {
            "title": "New Task",
            "description": "A new task description",
            "priority": "high",
            "assignee_id": str(employee_user.id),
            "building_id": str(building.id),
        }
        
        response = await client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json=task_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_task_as_employee_returns_403(self, client, employee_user, building):
        """Employee cannot create tasks."""
        token = create_auth_token("employee@example.com", "employee")
        task_data = {
            "title": "Unauthorized Task",
            "description": "Should not be created",
            "building_id": str(building.id),
        }
        
        response = await client.post(
            "/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json=task_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_task_without_auth_returns_401(self, client, building):
        """Unauthenticated user cannot create tasks."""
        task_data = {
            "title": "Anonymous Task",
            "description": "Should not be created",
            "building_id": str(building.id),
        }
        
        response = await client.post(
            "/tasks",
            json=task_data,
        )
        
        assert response.status_code == 401


class TestGetTask:
    """Test GET /tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_as_manager(self, client, manager_user, sample_task):
        """Manager can get any task."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/tasks/{sample_task.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_task.id)
        assert data["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_assigned_task_as_employee(self, client, employee_user, sample_task):
        """Employee can get their assigned task."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            f"/tasks/{sample_task.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_task.id)

    @pytest.mark.asyncio
    async def test_get_nonexistent_task_returns_404(self, client, manager_user):
        """Getting non-existent task returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/tasks/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestAssignTask:
    """Test PATCH /tasks/{task_id}/assign endpoint."""

    @pytest.mark.asyncio
    async def test_assign_task_as_manager(self, client, test_setup, manager_user, employee_user, sample_task):
        """Manager can assign a task."""
        engine, TestingSessionLocal = test_setup
        token = create_auth_token("manager@example.com", "manager")
        
        # Create a new employee to assign to
        async with TestingSessionLocal() as session:
            new_employee = User(
                email="newemployee@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="New",
                last_name="Employee",
                role="employee",
                is_active=True,
            )
            session.add(new_employee)
            await session.commit()
            await session.refresh(new_employee)
        
        assign_data = {"assignee_id": str(new_employee.id)}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/assign",
            headers={"Authorization": f"Bearer {token}"},
            json=assign_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assignee_id"] == str(new_employee.id)

    @pytest.mark.asyncio
    async def test_assign_task_as_employee_returns_403(self, client, employee_user, sample_task):
        """Employee cannot assign tasks."""
        token = create_auth_token("employee@example.com", "employee")
        assign_data = {"assignee_id": str(employee_user.id)}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/assign",
            headers={"Authorization": f"Bearer {token}"},
            json=assign_data,
        )
        
        assert response.status_code == 403


class TestUpdateTaskStatus:
    """Test PATCH /tasks/{task_id}/status endpoint."""

    @pytest.mark.asyncio
    async def test_employee_updates_status_to_in_progress(self, client, employee_user, sample_task):
        """Employee can start a task."""
        token = create_auth_token("employee@example.com", "employee")
        status_data = {"status": "in_progress"}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json=status_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_employee_updates_status_to_completed(self, client, employee_user, sample_task):
        """Employee can mark task as completed."""
        # First set to in_progress via API (employee can do this)
        token = create_auth_token("employee@example.com", "employee")
        
        # First update to in_progress
        progress_response = await client.patch(
            f"/tasks/{sample_task.id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "in_progress"},
        )
        assert progress_response.status_code == 200
        
        # Then update to completed
        status_data = {"status": "completed"}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json=status_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_manager_updates_any_status(self, client, manager_user, sample_task):
        """Manager can update to any status."""
        token = create_auth_token("manager@example.com", "manager")
        status_data = {"status": "cancelled"}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json=status_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"


class TestVerifyTask:
    """Test PATCH /tasks/{task_id}/verify endpoint."""

    @pytest.mark.asyncio
    async def test_manager_verifies_completion(self, client, test_setup, manager_user, employee_user, building):
        """Manager can verify task completion."""
        engine, TestingSessionLocal = test_setup
        # Create a completed task
        async with TestingSessionLocal() as session:
            completed_task = Task(
                title="Completed Task",
                description="To be verified",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.NORMAL,
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
                building_id=building.id,
            )
            session.add(completed_task)
            await session.commit()
            await session.refresh(completed_task)
            task_id = completed_task.id
        
        token = create_auth_token("manager@example.com", "manager")
        verify_data = {"approved": True}
        
        response = await client.patch(
            f"/tasks/{task_id}/verify",
            headers={"Authorization": f"Bearer {token}"},
            json=verify_data,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_manager_rejects_with_reason(self, client, test_setup, manager_user, employee_user, building):
        """Manager can reject task completion with reason."""
        engine, TestingSessionLocal = test_setup
        # Create a completed task
        async with TestingSessionLocal() as session:
            completed_task = Task(
                title="Task to Reject",
                description="To be rejected",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.NORMAL,
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
                building_id=building.id,
            )
            session.add(completed_task)
            await session.commit()
            await session.refresh(completed_task)
            task_id = completed_task.id
        
        token = create_auth_token("manager@example.com", "manager")
        verify_data = {
            "approved": False,
            "rejection_reason": "Need more work",
        }
        
        response = await client.patch(
            f"/tasks/{task_id}/verify",
            headers={"Authorization": f"Bearer {token}"},
            json=verify_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "on_hold"
        assert data["rejection_reason"] == "Need more work"

    @pytest.mark.asyncio
    async def test_employee_cannot_verify(self, client, employee_user, sample_task):
        """Employee cannot verify tasks."""
        token = create_auth_token("employee@example.com", "employee")
        verify_data = {"approved": True}
        
        response = await client.patch(
            f"/tasks/{sample_task.id}/verify",
            headers={"Authorization": f"Bearer {token}"},
            json=verify_data,
        )
        
        assert response.status_code == 403


class TestDeleteTask:
    """Test DELETE /tasks/{task_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task_as_manager(self, client, test_setup, manager_user, employee_user, building):
        """Manager can delete a task."""
        engine, TestingSessionLocal = test_setup
        # Create a task to delete
        async with TestingSessionLocal() as session:
            task_to_delete = Task(
                title="Task to Delete",
                description="Will be deleted",
                status=TaskStatus.PENDING,
                priority=TaskPriority.LOW,
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
                building_id=building.id,
            )
            session.add(task_to_delete)
            await session.commit()
            await session.refresh(task_to_delete)
            task_id = task_to_delete.id
        
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_task_as_employee_returns_403(self, client, employee_user, sample_task):
        """Employee cannot delete tasks."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.delete(
            f"/tasks/{sample_task.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task_returns_404(self, client, manager_user):
        """Deleting non-existent task returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            "/tasks/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestUnauthorizedAccess:
    """Test access without proper authorization."""

    @pytest.mark.asyncio
    async def test_access_without_token_returns_401(self, client):
        """Accessing protected endpoints without token returns 401."""
        response = await client.get("/tasks")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_with_invalid_token_returns_401(self, client):
        """Accessing with invalid token returns 401."""
        response = await client.get(
            "/tasks",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
