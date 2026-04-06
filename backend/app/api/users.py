"""User management API endpoints with RBAC."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdate, UserListResponse
from app.dependencies.auth import (
    get_current_active_user,
    require_role,
    get_current_manager_only,
)
from app.crud.user import (
    get_user_by_id,
    get_users,
    update_user,
    delete_user as soft_delete_user,
)


router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager_only),
):
    """List all users with pagination and filtering (manager only).
    
    Args:
        skip: Number of records to skip.
        limit: Maximum records to return.
        role: Filter by user role (optional).
        is_active: Filter by active status (optional).
        db: Database session.
        current_user: Current authenticated manager user.
        
    Returns:
        UserListResponse with paginated users.
    """
    users, total = await get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )
    
    return UserListResponse(
        items=[
            UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
            )
            for user in users
        ],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get user by ID.
    
    - Managers can get any user
    - Users can only get their own profile
    
    Args:
        user_id: User UUID to retrieve.
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        UserResponse for the requested user.
        
    Raises:
        HTTPException: 403 if not authorized, 404 if user not found.
    """
    # Check authorization
    if current_user.role not in ["super_admin", "manager"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's data",
        )
    
    # Get user from database
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: str,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update user profile.
    
    - Users can update their own profile
    - Managers can update any user's profile
    
    Args:
        user_id: User UUID to update.
        update_data: Fields to update (partial update).
        db: Database session.
        current_user: Current authenticated user.
        
    Returns:
        UserResponse with updated user data.
        
    Raises:
        HTTPException: 403 if not authorized, 404 if user not found.
    """
    # Check authorization
    if current_user.role not in ["super_admin", "manager"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another user's data",
        )
    
    # Get user from database
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user
    updated_user = await update_user(db, user, update_data)
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        phone=updated_user.phone,
        role=updated_user.role,
        is_active=updated_user.is_active,
    )


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user_endpoint(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_manager_only),
):
    """Soft delete user by setting is_active to False (manager only).
    
    Args:
        user_id: User UUID to delete.
        db: Database session.
        current_user: Current authenticated manager user.
        
    Returns:
        UserResponse with deleted user data (is_active=False).
        
    Raises:
        HTTPException: 403 if not manager, 404 if user not found.
    """
    # Get user from database
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Soft delete (set is_active=False)
    deleted_user = await soft_delete_user(db, user)
    
    return UserResponse(
        id=deleted_user.id,
        email=deleted_user.email,
        first_name=deleted_user.first_name,
        last_name=deleted_user.last_name,
        phone=deleted_user.phone,
        role=deleted_user.role,
        is_active=deleted_user.is_active,
    )
