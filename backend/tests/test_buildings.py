"""Building endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key-for-building-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.building import Building
from app.models.apartment import Apartment
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
async def sample_building(test_db):
    """Create a sample building."""
    async with TestingSessionLocal() as session:
        building = Building(
            name="Test Building",
            address="123 Test Street",
            city="Budapest",
            postal_code="1000",
            country="Hungary",
            description="A test building",
        )
        session.add(building)
        await session.commit()
        await session.refresh(building)
        return building


class TestListBuildings:
    """Test GET /buildings endpoint with RBAC."""

    @pytest.mark.asyncio
    async def test_list_buildings_as_manager_returns_200(self, client, manager_user, sample_building):
        """Manager can list all buildings."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/buildings",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_buildings_as_employee_returns_403(self, client, employee_user):
        """Employee cannot list buildings."""
        token = create_auth_token("employee@example.com", "employee")
        response = await client.get(
            "/buildings",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_buildings_without_auth_returns_401(self, client):
        """Unauthenticated user cannot list buildings."""
        response = await client.get("/buildings")
        
        assert response.status_code == 401


class TestGetBuilding:
    """Test GET /buildings/{building_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_building_as_manager(self, client, manager_user, sample_building):
        """Manager can get any building."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Building"
        assert data["address"] == "123 Test Street"
        assert data["city"] == "Budapest"

    @pytest.mark.asyncio
    async def test_get_nonexistent_building_returns_404(self, client, manager_user):
        """Getting non-existent building returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/buildings/nonexistent-id-12345",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestCreateBuilding:
    """Test POST /buildings endpoint."""

    @pytest.mark.asyncio
    async def test_create_building_as_manager(self, client, manager_user):
        """Manager can create a building."""
        token = create_auth_token("manager@example.com", "manager")
        building_data = {
            "name": "New Building",
            "address": "456 New Street",
            "city": "Budapest",
            "postal_code": "2000",
            "country": "Hungary",
            "description": "A new building",
        }
        
        response = await client.post(
            "/buildings",
            headers={"Authorization": f"Bearer {token}"},
            json=building_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Building"
        assert data["address"] == "456 New Street"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_building_as_employee_returns_403(self, client, employee_user):
        """Employee cannot create buildings."""
        token = create_auth_token("employee@example.com", "employee")
        building_data = {
            "name": "New Building",
            "address": "456 New Street",
            "city": "Budapest",
        }
        
        response = await client.post(
            "/buildings",
            headers={"Authorization": f"Bearer {token}"},
            json=building_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_building_without_required_fields_returns_422(self, client, manager_user):
        """Creating building without required fields returns 422."""
        token = create_auth_token("manager@example.com", "manager")
        building_data = {
            "name": "Incomplete Building",
            # Missing address and city
        }
        
        response = await client.post(
            "/buildings",
            headers={"Authorization": f"Bearer {token}"},
            json=building_data,
        )
        
        assert response.status_code == 422


class TestUpdateBuilding:
    """Test PATCH /buildings/{building_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_building_as_manager(self, client, manager_user, sample_building):
        """Manager can update a building."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {"name": "Updated Building Name", "description": "Updated description"}
        
        response = await client.patch(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Building Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_building_as_employee_returns_403(self, client, employee_user, sample_building):
        """Employee cannot update buildings."""
        token = create_auth_token("employee@example.com", "employee")
        update_data = {"name": "Hacked Name"}
        
        response = await client.patch(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_building_returns_404(self, client, manager_user):
        """Updating non-existent building returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.patch(
            "/buildings/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Test"},
        )
        
        assert response.status_code == 404


class TestDeleteBuilding:
    """Test DELETE /buildings/{building_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_building_as_manager(self, client, manager_user, sample_building):
        """Manager can delete a building."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_building_as_employee_returns_403(self, client, employee_user, sample_building):
        """Employee cannot delete buildings."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.delete(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_building_with_apartments_returns_400(self, client, manager_user, sample_building, owner_user):
        """Cannot delete building that has apartments."""
        # Create an apartment in the building
        async with TestingSessionLocal() as session:
            apartment = Apartment(
                building_id=sample_building.id,
                unit_number="101",
                floor=1,
                owner_id=owner_user.id,
                square_meters=50.5,
            )
            session.add(apartment)
            await session.commit()
        
        token = create_auth_token("manager@example.com", "manager")
        response = await client.delete(
            f"/buildings/{sample_building.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_nonexistent_building_returns_404(self, client, manager_user):
        """Deleting non-existent building returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            "/buildings/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404
