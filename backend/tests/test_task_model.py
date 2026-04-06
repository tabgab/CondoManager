"""Task model tests - TDD approach."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

os.environ["SECRET_KEY"] = "test-secret-key-for-task-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.building import Building
from app.models.apartment import Apartment
from app.models.report import Report
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_update import TaskUpdate


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def manager_user(test_db):
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
async def employee_user(test_db):
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
async def sample_building(test_db):
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


class TestTaskModel:
    """Test Task model creation and fields."""

    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(self, manager_user, employee_user, sample_building):
        """Test creating a task with all fields populated."""
        async with TestingSessionLocal() as session:
            task = Task(
                title="Fix leaking pipe",
                description="The pipe in apartment 101 is leaking",
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
                building_id=sample_building.id,
                estimated_hours=2.5,
                due_date=datetime.utcnow() + timedelta(days=7),
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            assert task.id is not None
            assert task.title == "Fix leaking pipe"
            assert task.status == TaskStatus.PENDING
            assert task.priority == TaskPriority.HIGH
            assert task.created_by_id == manager_user.id
            assert task.assignee_id == employee_user.id
            assert task.building_id == sample_building.id
            assert task.estimated_hours == 2.5
            assert task.due_date is not None
            assert task.created_at is not None
            assert task.updated_at is not None

    @pytest.mark.asyncio
    async def test_task_status_transitions(self, manager_user, employee_user):
        """Test task status can be updated."""
        async with TestingSessionLocal() as session:
            task = Task(
                title="Clean hallway",
                description="Weekly cleaning",
                status=TaskStatus.PENDING,
                priority=TaskPriority.NORMAL,
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            # Transition to in_progress
            task.status = TaskStatus.IN_PROGRESS
            await session.commit()
            await session.refresh(task)
            assert task.status == TaskStatus.IN_PROGRESS
            
            # Transition to completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            await session.commit()
            await session.refresh(task)
            assert task.status == TaskStatus.COMPLETED
            assert task.completed_at is not None

    @pytest.mark.asyncio
    async def test_task_assignee_relationship(self, manager_user, employee_user):
        """Test task assignee relationship."""
        async with TestingSessionLocal() as session:
            task = Task(
                title="Test task",
                description="Test description",
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
            )
            session.add(task)
            await session.commit()
            
            # Load task with assignee
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            result = await session.execute(
                select(Task).where(Task.id == task.id).options(selectinload(Task.assignee))
            )
            loaded_task = result.scalar_one()
            
            assert loaded_task.assignee is not None
            assert loaded_task.assignee.email == "employee@example.com"

    @pytest.mark.asyncio
    async def test_task_report_link(self, manager_user, employee_user, sample_building):
        """Test linking task to a report."""
        async with TestingSessionLocal() as session:
            # Create a report first
            report = Report(
                reporter_id=manager_user.id,
                building_id=sample_building.id,
                title="Pipe leak",
                description="Water leaking",
                category="maintenance",
                priority="high",
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            
            # Create task from report
            task = Task(
                title="Fix pipe leak",
                description="Fix the reported pipe leak",
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
                report_id=report.id,
                building_id=sample_building.id,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            assert task.report_id == report.id


class TestTaskUpdateModel:
    """Test TaskUpdate model for progress tracking."""

    @pytest.mark.asyncio
    async def test_create_task_update(self, manager_user, employee_user):
        """Test creating a task update."""
        async with TestingSessionLocal() as session:
            task = Task(
                title="Test task",
                description="Test",
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            update = TaskUpdate(
                task_id=task.id,
                author_id=employee_user.id,
                content="Started working on the task",
                percentage_complete=25,
            )
            session.add(update)
            await session.commit()
            await session.refresh(update)
            
            assert update.id is not None
            assert update.task_id == task.id
            assert update.content == "Started working on the task"
            assert update.percentage_complete == 25
            assert not update.is_concern
            assert not update.requires_manager_attention

    @pytest.mark.asyncio
    async def test_create_concern_update(self, manager_user, employee_user):
        """Test creating a concern update."""
        async with TestingSessionLocal() as session:
            task = Task(
                title="Test task",
                description="Test",
                created_by_id=manager_user.id,
                assignee_id=employee_user.id,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            concern = TaskUpdate(
                task_id=task.id,
                author_id=employee_user.id,
                content="Need more materials",
                is_concern=True,
                requires_manager_attention=True,
            )
            session.add(concern)
            await session.commit()
            
            assert concern.is_concern
            assert concern.requires_manager_attention


class TestTaskPriority:
    """Test task priority levels."""

    @pytest.mark.asyncio
    async def test_task_priority_levels(self, manager_user):
        """Test all priority levels can be set."""
        async with TestingSessionLocal() as session:
            for priority in [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH, TaskPriority.URGENT]:
                task = Task(
                    title=f"Task with {priority} priority",
                    description="Test",
                    created_by_id=manager_user.id,
                    priority=priority,
                )
                session.add(task)
                await session.commit()
                await session.refresh(task)
                assert task.priority == priority
