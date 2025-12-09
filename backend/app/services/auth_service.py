"""
Authentication Service

Handles password hashing, JWT token generation/validation,
and authentication-related utilities.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24  # 24 hours


class AuthService:
    """Authentication service for password and token management"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Bcrypt hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash

        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hash to verify against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength

        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"

        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"

        return True, None

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in token (should include user_id, email, role)
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload if valid, None if invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                return None

            if datetime.utcnow() > datetime.fromtimestamp(exp):
                return None

            # Check token type
            if payload.get("type") != "access":
                return None

            return payload

        except JWTError:
            return None

    @staticmethod
    def generate_password_reset_token() -> str:
        """
        Generate a secure random token for password reset

        Returns:
            URL-safe random token (32 bytes = 43 chars base64)
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure random API key

        Returns:
            URL-safe random key (48 bytes = 64 chars base64)
        """
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token or API key for storage

        Uses the same bcrypt hashing as passwords for consistency

        Args:
            token: Token to hash

        Returns:
            Bcrypt hash of the token
        """
        return pwd_context.hash(token)

    @staticmethod
    def verify_token_hash(token: str, token_hash: str) -> bool:
        """
        Verify a token against its hash

        Args:
            token: Plain token
            token_hash: Bcrypt hash to verify against

        Returns:
            True if token matches hash, False otherwise
        """
        return pwd_context.verify(token, token_hash)


# Singleton instance
auth_service = AuthService()
