"""User CRUD operations."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.auth import UserCreate
from app.schemas.user import UserUpdate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email address.
    
    Args:
        db: Async database session.
        email: User email to look up.
        
    Returns:
        User instance or None if not found.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Get user by ID.
    
    Args:
        db: Async database session.
        user_id: User UUID string.
        
    Returns:
        User instance or None if not found.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[User], int]:
    """Get list of users with optional filtering and pagination.
    
    Args:
        db: Async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        role: Filter by role (optional).
        is_active: Filter by active status (optional).
        
    Returns:
        Tuple of (list of users, total count).
    """
    # Build query
    query = select(User)
    count_query = select(func.count()).select_from(User)
    
    # Apply filters
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
        count_query = count_query.where(User.is_active == is_active)
    
    # Execute count query
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Execute paginated query
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return list(users), total


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user with hashed password.
    
    Args:
        db: Async database session.
        user_data: User creation data.
        
    Returns:
        Created User instance.
    """
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=True,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def update_user(
    db: AsyncSession,
    user: User,
    update_data: UserUpdate,
) -> User:
    """Update user fields.
    
    Args:
        db: Async database session.
        user: User instance to update.
        update_data: UserUpdate with fields to update.
        
    Returns:
        Updated User instance.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def delete_user(db: AsyncSession, user: User) -> User:
    """Soft delete user by setting is_active to False.
    
    Args:
        db: Async database session.
        user: User instance to delete.
        
    Returns:
        Updated User instance.
    """
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate user by email and password.
    
    Args:
        db: Async database session.
        email: User email.
        password: Plain text password.
        
    Returns:
        User instance if authentication succeeds, None otherwise.
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
