"""Base model and database configuration for async SQLAlchemy."""
import os
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid


# Detect if using SQLite (for testing) or PostgreSQL (production)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://condomanager:condomanager@localhost:5432/condomanager"
)

# Supabase and most providers give postgresql:// but async SQLAlchemy needs postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

IS_SQLITE = "sqlite" in DATABASE_URL.lower()


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models with async support."""
    
    # Use String for UUID in SQLite, native UUID in PostgreSQL
    id_type = String if IS_SQLITE else PG_UUID
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Test-specific database setup
def get_test_engine():
    """Create a test engine using SQLite."""
    test_url = "sqlite+aiosqlite:///:memory:"
    return create_async_engine(test_url, echo=False, future=True)


def get_test_session_factory(test_engine):
    """Create test session factory."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
