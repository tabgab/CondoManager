"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.models.base import get_db
from app.crud.user import get_user_by_email, authenticate_user, create_user
from app.schemas.auth import (
    TokenRequest,
    TokenResponse,
    RefreshRequest,
    UserCreate,
    UserResponse,
    UserLoginResponse,
)
from app.models.user import User


router = APIRouter()
settings = get_settings()

# OAuth2 scheme for token extraction
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
    
    if not user.is_active:
        raise credentials_exception
    
    return user


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: TokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens.
    
    Args:
        request: TokenRequest with email and password.
        db: Database session.
        
    Returns:
        UserLoginResponse with access token, refresh token, and user info.
        
    Raises:
        HTTPException: 401 if authentication fails.
    """
    user = await authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens with user info
    token_data = {"sub": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user.email})
    
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
):
    """Refresh access token using refresh token.
    
    Args:
        request: Refresh token request containing the refresh token.
        
    Returns:
        TokenResponse with new access token.
        
    Raises:
        HTTPException: 401 if refresh token is invalid.
    """
    payload = verify_token(request.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    token_data = {"sub": email}
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Keep same refresh token
        token_type="bearer",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user.
    
    Args:
        user_data: User creation data.
        db: Database session.
        
    Returns:
        UserResponse for the created user.
        
    Raises:
        HTTPException: 409 if email already exists.
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Create user
    user = await create_user(db, user_data)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info.
    
    Args:
        current_user: User from get_current_user dependency.
        
    Returns:
        UserResponse for the authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
    )
