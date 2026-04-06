"""Tests for User model - TDD approach."""
import os
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set SQLite for testing before importing models
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.models.user import User, UserRole
from app.models.base import Base
from app.core.security import get_password_hash, verify_password


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test using SQLite."""
    # Create engine and tables
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


class TestUserModel:
    """Test suite for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a basic user."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            first_name="John",
            last_name="Doe",
            role=UserRole.OWNER.value
        )
        db_session.add(user)
        await db_session.commit()
        
        result = await db_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        saved_user = result.scalar_one_or_none()
        
        assert saved_user is not None
        assert saved_user.email == "test@example.com"
        assert saved_user.first_name == "John"
        assert saved_user.last_name == "Doe"
        assert saved_user.role == UserRole.OWNER.value
        assert saved_user.is_active is True
        assert saved_user.id is not None
        assert len(saved_user.id) == 36  # UUID string

    @pytest.mark.asyncio
    async def test_email_uniqueness(self, db_session: AsyncSession):
        """Test that email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("password1"),
            first_name="User",
            last_name="One",
            role=UserRole.OWNER.value
        )
        db_session.add(user1)
        await db_session.commit()
        
        user2 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("password2"),
            first_name="User",
            last_name="Two",
            role=UserRole.TENANT.value
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_password_hashing(self):
        """Test password hashing and verification."""
        plain_password = "my_secure_password"
        hashed = get_password_hash(plain_password)
        
        assert hashed != plain_password
        assert verify_password(plain_password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    @pytest.mark.asyncio
    async def test_user_roles(self, db_session: AsyncSession):
        """Test all user roles work correctly."""
        roles = [
            UserRole.SUPER_ADMIN.value,
            UserRole.MANAGER.value,
            UserRole.EMPLOYEE.value,
            UserRole.OWNER.value,
            UserRole.TENANT.value
        ]
        
        for i, role in enumerate(roles):
            user = User(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("pass"),
                first_name=f"User{i}",
                last_name="Test",
                role=role
            )
            db_session.add(user)
        
        await db_session.commit()
        
        result = await db_session.execute(select(User))
        users = result.scalars().all()
        assert len(users) == 5

    @pytest.mark.asyncio
    async def test_optional_phone(self, db_session: AsyncSession):
        """Test phone field is optional."""
        user_without_phone = User(
            email="nophone@example.com",
            hashed_password=get_password_hash("pass"),
            first_name="No",
            last_name="Phone",
            role=UserRole.OWNER.value
        )
        db_session.add(user_without_phone)
        await db_session.commit()
        
        result = await db_session.execute(
            select(User).where(User.email == "nophone@example.com")
        )
        saved_user = result.scalar_one()
        assert saved_user.phone is None

    @pytest.mark.asyncio
    async def test_user_with_phone(self, db_session: AsyncSession):
        """Test user can have phone number."""
        user_with_phone = User(
            email="withphone@example.com",
            hashed_password=get_password_hash("pass"),
            first_name="With",
            last_name="Phone",
            phone="+1234567890",
            role=UserRole.OWNER.value
        )
        db_session.add(user_with_phone)
        await db_session.commit()
        
        result = await db_session.execute(
            select(User).where(User.email == "withphone@example.com")
        )
        saved_user = result.scalar_one()
        assert saved_user.phone == "+1234567890"
