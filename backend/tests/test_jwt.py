"""Tests for JWT token handling - TDD approach."""
import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta, timezone

# Set test secret before importing JWT module
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-testing"

from app.core.jwt import create_access_token, create_refresh_token, verify_token


class TestJWT:
    """Test suite for JWT token operations."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a valid JWT string."""
        data = {"sub": "user@example.com", "role": "owner"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT has 3 parts separated by dots

    def test_create_refresh_token_returns_string(self):
        """Test that create_refresh_token returns a valid JWT string."""
        data = {"sub": "user@example.com"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2

    def test_verify_token_returns_payload(self):
        """Test that verify_token decodes and returns the original payload."""
        data = {"sub": "user@example.com", "role": "manager"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user@example.com"
        assert payload["role"] == "manager"

    def test_verify_token_returns_none_for_invalid_token(self):
        """Test that verify_token returns None for invalid/malformed tokens."""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token)
        
        assert result is None

    def test_verify_token_returns_none_for_empty_token(self):
        """Test that verify_token returns None for empty string."""
        result = verify_token("")
        
        assert result is None

    def test_access_token_has_expiration(self):
        """Test that access token includes exp claim."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert "exp" in payload
        # Expiration should be in the future
        exp_timestamp = payload["exp"]
        now = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now

    def test_refresh_token_has_longer_expiration(self):
        """Test that refresh token has longer expiration than access token."""
        data = {"sub": "user@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)
        
        assert access_payload is not None
        assert refresh_payload is not None
        
        # Refresh token should expire later than access token
        assert refresh_payload["exp"] > access_payload["exp"]

    def test_access_token_default_expiration_is_30_minutes(self):
        """Test that access token expires in approximately 30 minutes."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        
        exp_timestamp = payload["exp"]
        now = datetime.now(timezone.utc).timestamp()
        
        # Should expire between 29 and 31 minutes from now
        minutes_until_exp = (exp_timestamp - now) / 60
        assert 29 <= minutes_until_exp <= 31

    def test_refresh_token_default_expiration_is_7_days(self):
        """Test that refresh token expires in approximately 7 days."""
        data = {"sub": "user@example.com"}
        token = create_refresh_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        
        exp_timestamp = payload["exp"]
        now = datetime.now(timezone.utc).timestamp()
        
        # Should expire between 6.9 and 7.1 days from now
        days_until_exp = (exp_timestamp - now) / (24 * 3600)
        assert 6.9 <= days_until_exp <= 7.1

    def test_different_tokens_for_same_data(self):
        """Test that access and refresh tokens are different for same data."""
        data = {"sub": "user@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        # Tokens should be different strings
        assert access_token != refresh_token

    def test_custom_expiry_minutes(self):
        """Test creating token with custom expiration."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data, expires_minutes=60)
        
        payload = verify_token(token)
        assert payload is not None
        
        exp_timestamp = payload["exp"]
        now = datetime.now(timezone.utc).timestamp()
        
        # Should expire in approximately 60 minutes
        minutes_until_exp = (exp_timestamp - now) / 60
        assert 59 <= minutes_until_exp <= 61
