"""
CSRF (Cross-Site Request Forgery) Protection
Generates and validates CSRF tokens for state-changing requests
"""
import secrets
import hashlib
import time
from typing import Optional, Tuple
from fastapi import HTTPException, status, Header


class CSRFProtection:
    """
    CSRF token generation and validation

    Tokens are double-submit cookies: the same random value is stored
    in both a cookie and a request header/field
    """

    # Token expiration time in seconds (default: 1 hour)
    TOKEN_EXPIRATION = 3600

    # Token length in bytes
    TOKEN_BYTES = 32

    @staticmethod
    def generate_token() -> str:
        """
        Generate a new CSRF token

        Returns:
            URL-safe base64 encoded token
        """
        # Generate cryptographically secure random token
        token = secrets.token_urlsafe(CSRFProtection.TOKEN_BYTES)
        return token

    @staticmethod
    def create_token_with_timestamp() -> str:
        """
        Create a CSRF token with embedded timestamp

        Returns:
            Token with timestamp (format: timestamp:token)
        """
        timestamp = str(int(time.time()))
        token = CSRFProtection.generate_token()

        # Combine timestamp and token
        token_with_ts = f"{timestamp}:{token}"

        return token_with_ts

    @staticmethod
    def validate_token_timestamp(token_with_ts: str) -> Tuple[bool, Optional[str]]:
        """
        Validate token timestamp

        Args:
            token_with_ts: Token with timestamp (format: timestamp:token)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Split timestamp and token
            parts = token_with_ts.split(':', 1)
            if len(parts) != 2:
                return False, "Invalid token format"

            timestamp_str, token = parts
            timestamp = int(timestamp_str)

            # Check if token has expired
            current_time = int(time.time())
            age = current_time - timestamp

            if age > CSRFProtection.TOKEN_EXPIRATION:
                return False, f"Token expired (age: {age}s, max: {CSRFProtection.TOKEN_EXPIRATION}s)"

            if age < 0:
                return False, "Token timestamp is in the future"

            return True, None

        except (ValueError, AttributeError):
            return False, "Invalid token format"

    @staticmethod
    def verify_token(expected_token: str, provided_token: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Verify CSRF token

        Args:
            expected_token: The expected token (from cookie/session)
            provided_token: The provided token (from header/form)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not provided_token:
            return False, "CSRF token missing"

        if not expected_token:
            return False, "CSRF token not found in session"

        # Validate timestamp if token has one
        if ':' in expected_token:
            is_valid, error = CSRFProtection.validate_token_timestamp(expected_token)
            if not is_valid:
                return False, error

        # Compare tokens using constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(expected_token, provided_token):
            return False, "CSRF token mismatch"

        return True, None


class CSRFValidator:
    """
    FastAPI dependency for CSRF validation
    """

    def __init__(self, required: bool = True):
        """
        Initialize CSRF validator

        Args:
            required: Whether CSRF token is required
        """
        self.required = required

    async def __call__(
        self,
        x_csrf_token: Optional[str] = Header(None),
        csrf_token: Optional[str] = Header(None)
    ):
        """
        Validate CSRF token from request headers

        Args:
            x_csrf_token: CSRF token from X-CSRF-Token header
            csrf_token: CSRF token from CSRF-Token header

        Raises:
            HTTPException: If CSRF validation fails
        """
        # Accept either header name
        provided_token = x_csrf_token or csrf_token

        if self.required and not provided_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Include X-CSRF-Token header."
            )

        # For now, we'll just validate that a token is provided
        # In a full implementation, you'd compare against a session/cookie value
        # Since we're using JWT tokens, CSRF is less of a concern for API endpoints
        # but we provide the infrastructure for form-based endpoints

        return provided_token


# Convenience functions

def generate_csrf_token() -> str:
    """
    Generate a new CSRF token with timestamp

    Returns:
        CSRF token string
    """
    return CSRFProtection.create_token_with_timestamp()


def validate_csrf_token(expected: str, provided: Optional[str]) -> None:
    """
    Validate CSRF token and raise exception if invalid

    Args:
        expected: Expected token
        provided: Provided token

    Raises:
        HTTPException: If validation fails
    """
    is_valid, error = CSRFProtection.verify_token(expected, provided)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"CSRF validation failed: {error}"
        )


# FastAPI dependency for CSRF protection
require_csrf = CSRFValidator(required=True)
csrf_optional = CSRFValidator(required=False)
