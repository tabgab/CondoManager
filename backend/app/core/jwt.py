"""JWT token creation and verification utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError

from app.core.config import get_settings


# Get settings
settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Default token expiration times
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode (e.g., {"sub": user_email}).
        expires_minutes: Minutes until expiration. Defaults to 30 minutes.
        
    Returns:
        str: Encoded JWT access token.
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_minutes is None:
        expires_minutes = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary containing claims to encode (e.g., {"sub": user_email}).
        
    Returns:
        str: Encoded JWT refresh token (expires in 7 days).
    """
    to_encode = data.copy()
    
    # Refresh tokens expire in 7 days
    expire = datetime.now(timezone.utc) + timedelta(days=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify.
        
    Returns:
        dict: Decoded token payload if valid, None if invalid or expired.
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    except Exception:
        return None
