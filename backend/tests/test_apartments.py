"""Apartment endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

os.environ["SECRET_KEY"] = "test-secret-key-for-apartment-tests"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.models.base import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.building import Building
from app.models.apartment import Apartment
from app.core.jwt import create_access_token


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


def create_auth_token(email: str, role: str) -> str:
    token_data = {"sub": email, "role": role}
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


@pytest_asyncio.fixture
async def employee_user(test_db):
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
async def tenant_user(test_db):
    async with TestingSessionLocal() as session:
        user = User(
            email="tenant@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="Tenant",
            last_name="User",
            role="tenant",
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
            description="A test building",
        )
        session.add(building)
        await session.commit()
        await session.refresh(building)
        return building


@pytest_asyncio.fixture
async def sample_apartment(test_db, sample_building, owner_user):
    async with TestingSessionLocal() as session:
        apartment = Apartment(
            building_id=sample_building.id,
            unit_number="101A",
            floor=1,
            owner_id=owner_user.id,
            square_meters=65.5,
        )
        session.add(apartment)
        await session.commit()
        await session.refresh(apartment)
        return apartment


class TestListApartments:
    """Test GET /buildings/{building_id}/apartments endpoint."""

    @pytest.mark.asyncio
    async def test_list_apartments_as_manager(self, client, manager_user, sample_building, sample_apartment):
        """Manager can list apartments in a building."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/buildings/{sample_building.id}/apartments",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["unit_number"] == "101A"

    @pytest.mark.asyncio
    async def test_list_apartments_as_owner_of_apartment(self, client, owner_user, sample_building, sample_apartment):
        """Owner can see their apartment(s) in the building."""
        token = create_auth_token("owner@example.com", "owner")
        response = await client.get(
            f"/buildings/{sample_building.id}/apartments",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_apartments_without_auth_returns_401(self, client, sample_building):
        """Unauthenticated user cannot list apartments."""
        response = await client.get(f"/buildings/{sample_building.id}/apartments")
        
        assert response.status_code == 401


class TestGetApartment:
    """Test GET /apartments/{apartment_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_apartment_as_manager(self, client, manager_user, sample_apartment):
        """Manager can get any apartment."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["unit_number"] == "101A"
        assert data["floor"] == 1
        assert data["square_meters"] == 65.5

    @pytest.mark.asyncio
    async def test_get_apartment_as_owner(self, client, owner_user, sample_apartment):
        """Owner can get their apartment."""
        token = create_auth_token("owner@example.com", "owner")
        response = await client.get(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["unit_number"] == "101A"

    @pytest.mark.asyncio
    async def test_get_apartment_as_tenant(self, client, tenant_user, sample_building):
        """Tenant can get apartment they're assigned to."""
        # First assign tenant to an apartment
        async with TestingSessionLocal() as session:
            apartment = Apartment(
                building_id=sample_building.id,
                unit_number="202B",
                floor=2,
                tenant_id=tenant_user.id,
                square_meters=50.0,
            )
            session.add(apartment)
            await session.commit()
            await session.refresh(apartment)
            apartment_id = apartment.id
        
        token = create_auth_token("tenant@example.com", "tenant")
        response = await client.get(
            f"/apartments/{apartment_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        assert response.json()["unit_number"] == "202B"

    @pytest.mark.asyncio
    async def test_get_nonexistent_apartment_returns_404(self, client, manager_user):
        """Getting non-existent apartment returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/apartments/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestCreateApartment:
    """Test POST /buildings/{building_id}/apartments endpoint."""

    @pytest.mark.asyncio
    async def test_create_apartment_as_manager(self, client, manager_user, sample_building, owner_user):
        """Manager can create an apartment."""
        token = create_auth_token("manager@example.com", "manager")
        apartment_data = {
            "unit_number": "305",
            "floor": 3,
            "owner_id": str(owner_user.id),
            "square_meters": 85.0,
        }
        
        response = await client.post(
            f"/buildings/{sample_building.id}/apartments",
            headers={"Authorization": f"Bearer {token}"},
            json=apartment_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["unit_number"] == "305"
        assert data["floor"] == 3
        assert data["square_meters"] == 85.0

    @pytest.mark.asyncio
    async def test_create_apartment_as_employee_returns_403(self, client, employee_user, sample_building, owner_user):
        """Employee cannot create apartments."""
        token = create_auth_token("employee@example.com", "employee")
        apartment_data = {
            "unit_number": "405",
            "floor": 4,
            "owner_id": str(owner_user.id),
            "square_meters": 60.0,
        }
        
        response = await client.post(
            f"/buildings/{sample_building.id}/apartments",
            headers={"Authorization": f"Bearer {token}"},
            json=apartment_data,
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_apartment_without_required_fields_returns_422(self, client, manager_user, sample_building):
        """Creating apartment without required fields returns 422."""
        token = create_auth_token("manager@example.com", "manager")
        apartment_data = {
            # Missing unit_number
            "floor": 3,
        }
        
        response = await client.post(
            f"/buildings/{sample_building.id}/apartments",
            headers={"Authorization": f"Bearer {token}"},
            json=apartment_data,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_apartment_in_nonexistent_building_returns_404(self, client, manager_user, owner_user):
        """Creating apartment in non-existent building returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        apartment_data = {
            "unit_number": "505",
            "owner_id": str(owner_user.id),
        }
        
        response = await client.post(
            "/buildings/nonexistent-id/apartments",
            headers={"Authorization": f"Bearer {token}"},
            json=apartment_data,
        )
        
        assert response.status_code == 404


class TestUpdateApartment:
    """Test PATCH /apartments/{apartment_id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_apartment_as_manager(self, client, manager_user, sample_apartment):
        """Manager can update any apartment."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {"unit_number": "Updated 101", "floor": 2}
        
        response = await client.patch(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["unit_number"] == "Updated 101"
        assert data["floor"] == 2

    @pytest.mark.asyncio
    async def test_update_own_apartment_as_owner(self, client, owner_user, sample_apartment):
        """Owner can update their own apartment details."""
        token = create_auth_token("owner@example.com", "owner")
        update_data = {"square_meters": 70.0}
        
        response = await client.patch(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["square_meters"] == 70.0

    @pytest.mark.asyncio
    async def test_update_other_apartment_as_owner_returns_403(self, client, owner_user, sample_building, tenant_user):
        """Owner cannot update another person's apartment."""
        # Create another apartment with tenant as owner
        async with TestingSessionLocal() as session:
            other_apartment = Apartment(
                building_id=sample_building.id,
                unit_number="999",
                owner_id=tenant_user.id,  # Different owner
                square_meters=50.0,
            )
            session.add(other_apartment)
            await session.commit()
            await session.refresh(other_apartment)
        
        token = create_auth_token("owner@example.com", "owner")
        response = await client.patch(
            f"/apartments/{other_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"unit_number": "Hacked"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_apartment_returns_404(self, client, manager_user):
        """Updating non-existent apartment returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.patch(
            "/apartments/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
            json={"unit_number": "Test"},
        )
        
        assert response.status_code == 404


class TestDeleteApartment:
    """Test DELETE /apartments/{apartment_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_apartment_as_manager(self, client, manager_user, sample_building, owner_user):
        """Manager can delete an apartment."""
        # Create an apartment to delete
        async with TestingSessionLocal() as session:
            apartment = Apartment(
                building_id=sample_building.id,
                unit_number="ToDelete",
                owner_id=owner_user.id,
            )
            session.add(apartment)
            await session.commit()
            await session.refresh(apartment)
            apartment_id = apartment.id
        
        token = create_auth_token("manager@example.com", "manager")
        response = await client.delete(
            f"/apartments/{apartment_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_apartment_as_owner_returns_403(self, client, owner_user, sample_apartment):
        """Owner cannot delete apartments."""
        token = create_auth_token("owner@example.com", "owner")
        
        response = await client.delete(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_apartment_as_employee_returns_403(self, client, employee_user, sample_apartment):
        """Employee cannot delete apartments."""
        token = create_auth_token("employee@example.com", "employee")
        
        response = await client.delete(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_apartment_returns_404(self, client, manager_user):
        """Deleting non-existent apartment returns 404."""
        token = create_auth_token("manager@example.com", "manager")
        
        response = await client.delete(
            "/apartments/nonexistent-id",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 404


class TestApartmentOwnership:
    """Test apartment owner/tenant assignment functionality."""

    @pytest.mark.asyncio
    async def test_apartment_includes_owner_info(self, client, manager_user, sample_apartment):
        """Apartment response includes owner information."""
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "owner" in data
        assert data["owner"]["email"] == "owner@example.com"
        assert data["owner"]["first_name"] == "Owner"

    @pytest.mark.asyncio
    async def test_assign_tenant_to_apartment(self, client, manager_user, sample_apartment, tenant_user):
        """Manager can assign a tenant to an apartment."""
        token = create_auth_token("manager@example.com", "manager")
        update_data = {"tenant_id": str(tenant_user.id)}
        
        response = await client.patch(
            f"/apartments/{sample_apartment.id}",
            headers={"Authorization": f"Bearer {token}"},
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tenant" in data
        assert data["tenant"]["email"] == "tenant@example.com"
