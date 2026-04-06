"""Authentication and RBAC dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.jwt import verify_token
from app.models.base import get_db
from app.crud.user import get_user_by_email, get_user_by_id
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token.
    
    Args:
        token: JWT bearer token from Authorization header.
        db: Database session.
        
    Returns:
        User instance if authenticated.
        
    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify user is active.
    
    Args:
        current_user: User from get_current_user dependency.
        
    Returns:
        User instance if active.
        
    Raises:
        HTTPException: 401 if user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """Dependency factory to require specific roles.
    
    Args:
        allowed_roles: List of role names that are allowed access.
        
    Returns:
        Dependency function that checks user role.
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}",
            )
        return current_user
    return role_checker


# Pre-built role-based dependencies
get_current_manager_only = require_role(["super_admin", "manager"])
get_current_active_manager = require_role(["super_admin", "manager"])

# Alias for require_manager - used by buildings/apartments endpoints
require_manager = require_role(["super_admin", "manager"])

async def require_owner_or_manager(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require user to be either the owner of the resource or a manager.
    
    Args:
        user_id: ID of the user being accessed.
        current_user: Current authenticated user.
        db: Database session.
        
    Returns:
        User instance if authorized.
        
    Raises:
        HTTPException: 403 if not authorized.
    """
    # Managers can access any user
    if current_user.role in ["super_admin", "manager"]:
        return current_user
    
    # Users can only access their own data
    if current_user.id == user_id:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cannot access another user's data",
    )
