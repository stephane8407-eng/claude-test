"""
Authentication Middleware

FastAPI dependencies for protecting routes and extracting current user.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.auth_service import auth_service

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Current authenticated User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token
    token = credentials.credentials

    # Verify token
    payload = auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user_id from token
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user (alias for clarity)

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current active user
    """
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin role

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if admin

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_village_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require village_admin or admin role

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        Current user if village admin or system admin

    Raises:
        HTTPException: 403 if user is not a village admin
    """
    if current_user.role not in ["admin", "village_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Village admin access required"
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, or None

    Useful for routes that work differently for authenticated vs anonymous users

    Args:
        credentials: Optional HTTP Bearer token
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        if payload is None:
            return None

        user_id = payload.get("user_id")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None

        return user

    except Exception:
        return None
