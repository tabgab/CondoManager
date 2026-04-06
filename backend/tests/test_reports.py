"""Report endpoint tests - TDD approach with RBAC."""
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

os.environ["SECRET_KEY"] = "test-secret-key-for-report-tests"
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


class TestListReports:
    """Test GET /reports endpoint with RBAC."""

    @pytest.mark.asyncio
    async def test_list_reports_as_manager_returns_200(self, client, manager_user, sample_apartment, owner_user):
        """Manager can list all reports."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="Test Report",
                description="Detailed description",
                category="maintenance",
                priority="high",
            )
            session.add(report)
            await session.commit()
        
        token = create_auth_token("manager@example.com", "manager")
        response = await client.get(
            "/reports",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_own_reports_as_owner(self, client, owner_user, sample_apartment):
        """Owner can see their own reports."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="My Report",
                description="My issue",
                category="cleaning",
                priority="medium",
            )
            session.add(report)
            await session.commit()
        
        token = create_auth_token("owner@example.com", "owner")
        response = await client.get(
            "/reports",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_reports_without_auth_returns_401(self, client):
        """Unauthenticated user cannot list reports."""
        response = await client.get("/reports")
        
        assert response.status_code == 401


class TestCreateReport:
    """Test POST /reports endpoint."""

    @pytest.mark.asyncio
    async def test_create_report_as_owner(self, client, owner_user, sample_apartment):
        """Owner can submit a report."""
        token = create_auth_token("owner@example.com", "owner")
        report_data = {
            "apartment_id": str(sample_apartment.id),
            "title": "Water leak in bathroom",
            "description": "There's a leak under the sink",
            "category": "maintenance",
            "priority": "high",
            "photo_urls": ["https://cloudinary.com/img1.jpg"],
        }
        
        response = await client.post(
            "/reports",
            headers={"Authorization": f"Bearer {token}"},
            json=report_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Water leak in bathroom"
        assert data["status"] == "pending"
        assert data["reporter_id"] == str(owner_user.id)

    @pytest.mark.asyncio
    async def test_create_report_as_tenant(self, client, tenant_user, sample_building):
        """Tenant can submit a report."""
        # Assign tenant to apartment
        from app.models.apartment import Apartment
        async with TestingSessionLocal() as session:
            apartment = Apartment(
                building_id=sample_building.id,
                unit_number="202",
                tenant_id=tenant_user.id,
            )
            session.add(apartment)
            await session.commit()
            await session.refresh(apartment)
            apt_id = apartment.id
        
        token = create_auth_token("tenant@example.com", "tenant")
        report_data = {
            "apartment_id": str(apt_id),
            "title": "Noisy neighbors",
            "description": "Loud music at night",
            "category": "noise",
            "priority": "medium",
        }
        
        response = await client.post(
            "/reports",
            headers={"Authorization": f"Bearer {token}"},
            json=report_data,
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_report_as_manager_returns_403(self, client, manager_user, sample_apartment):
        """Manager cannot submit reports (not an owner/tenant)."""
        token = create_auth_token("manager@example.com", "manager")
        report_data = {
            "apartment_id": str(sample_apartment.id),
            "title": "Test",
            "description": "Test description",
            "category": "other",
            "priority": "low",
        }
        
        response = await client.post(
            "/reports",
            headers={"Authorization": f"Bearer {token}"},
            json=report_data,
        )
        
        assert response.status_code == 403


class TestAcknowledgeReport:
    """Test PATCH /reports/{id}/acknowledge endpoint."""

    @pytest.mark.asyncio
    async def test_acknowledge_report_as_manager(self, client, manager_user, sample_apartment, owner_user):
        """Manager can acknowledge a report."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="Test Report",
                description="Test",
                category="maintenance",
                priority="high",
                status="pending",
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            report_id = report.id
        
        token = create_auth_token("manager@example.com", "manager")
        response = await client.patch(
            f"/reports/{report_id}/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"
        assert data["assigned_manager_id"] == str(manager_user.id)

    @pytest.mark.asyncio
    async def test_acknowledge_report_as_owner_returns_403(self, client, owner_user, sample_apartment):
        """Owner cannot acknowledge reports."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="Test Report",
                description="Test",
                category="maintenance",
                priority="high",
                status="pending",
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            report_id = report.id
        
        token = create_auth_token("owner@example.com", "owner")
        response = await client.patch(
            f"/reports/{report_id}/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 403


class TestRejectReport:
    """Test PATCH /reports/{id}/reject endpoint."""

    @pytest.mark.asyncio
    async def test_reject_report_as_manager(self, client, manager_user, sample_apartment, owner_user):
        """Manager can reject a report with reason."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="Test Report",
                description="Test",
                category="other",
                priority="low",
                status="pending",
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            report_id = report.id
        
        token = create_auth_token("manager@example.com", "manager")
        response = await client.patch(
            f"/reports/{report_id}/reject",
            headers={"Authorization": f"Bearer {token}"},
            json={"reason": "Duplicate report"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejection_reason"] == "Duplicate report"


class TestDeleteReport:
    """Test DELETE /reports/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_own_report_as_owner(self, client, owner_user, sample_apartment):
        """Owner can delete their own report."""
        from app.models.report import Report
        async with TestingSessionLocal() as session:
            report = Report(
                reporter_id=owner_user.id,
                apartment_id=sample_apartment.id,
                title="Test Report",
                description="Test",
                category="maintenance",
                priority="high",
                status="pending",
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)
            report_id = report.id
        
        token = create_auth_token("owner@example.com", "owner")
        response = await client.delete(
            f"/reports/{report_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 204
