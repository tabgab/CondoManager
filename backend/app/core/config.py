"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://condomanager:condomanager@localhost:5432/condomanager"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # App
    APP_NAME: str = "CondoManager"
    DEBUG: bool = False
    
    # Email Configuration
    EMAIL_PROVIDER: str = "sendgrid"  # sendgrid or resend
    SENDGRID_API_KEY: Optional[str] = None
    RESEND_API_KEY: Optional[str] = None
    DEFAULT_FROM_EMAIL: str = "noreply@condomanager.app"
    EMAIL_FROM_NAME: str = "CondoManager"
    
    # WebSocket Configuration
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Web Push Configuration (VAPID)
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_CLAIMS_SUB: str = "mailto:admin@condomanager.app"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
