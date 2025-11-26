"""
Authentication API Endpoints

Handles user registration, login, logout, password reset, and user profile.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, PasswordResetToken, Village
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_user, get_current_active_user

router = APIRouter()


# =====================================
# PYDANTIC SCHEMAS
# =====================================

class RegisterRequest(BaseModel):
    """Request body for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=12)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    village_slug: Optional[str] = None  # If provided, user becomes village_admin

class LoginRequest(BaseModel):
    """Request body for login"""
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    """Request body for password reset initiation"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Request body for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=12)

class TokenResponse(BaseModel):
    """Response containing access token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


# =====================================
# REGISTRATION
# =====================================

@router.post("/api/auth/register", tags=["Authentication"], response_model=TokenResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user

    - If village_slug is provided, user becomes a village_admin for that village
    - Otherwise, user is created with role 'user'
    - Password must meet strength requirements (12+ chars, upper, lower, digit)
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, error_message = auth_service.validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Determine role and village_id
    role = "user"
    village_id = None

    if request.village_slug:
        village = db.query(Village).filter(Village.slug == request.village_slug).first()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Village not found: {request.village_slug}"
            )

        # Check if village already has an admin
        existing_admin = db.query(User).filter(
            User.village_id == village.id,
            User.role == "village_admin"
        ).first()

        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Village {village.name} already has an admin"
            )

        role = "village_admin"
        village_id = village.id

    # Hash password
    password_hash = auth_service.hash_password(request.password)

    # Create user
    new_user = User(
        email=request.email,
        password_hash=password_hash,
        first_name=request.first_name,
        last_name=request.last_name,
        role=role,
        village_id=village_id,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    token_data = {
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }
    access_token = auth_service.create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=new_user.to_dict()
    )


# =====================================
# LOGIN
# =====================================

@router.post("/api/auth/login", tags=["Authentication"], response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password

    Returns JWT access token valid for 24 hours
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create access token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
    access_token = auth_service.create_access_token(token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user.to_dict()
    )


# =====================================
# LOGOUT
# =====================================

@router.post("/api/auth/logout", tags=["Authentication"])
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user

    Note: With JWT tokens, actual logout is handled client-side by discarding the token.
    This endpoint exists for consistency and future session management.
    """
    return {
        "message": "Successfully logged out",
        "user_id": current_user.id
    }


# =====================================
# GET CURRENT USER
# =====================================

@router.get("/api/auth/me", tags=["Authentication"])
def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile

    Requires valid JWT token in Authorization header
    """
    return current_user.to_dict()


# =====================================
# PASSWORD RESET
# =====================================

@router.post("/api/auth/reset-password-request", tags=["Authentication"])
def reset_password_request(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset

    Generates a reset token and would typically send it via email.
    For now, returns the token in the response (for testing).
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Don't reveal if user exists - return success anyway
        return {
            "message": "If the email exists, a password reset link has been sent"
        }

    # Generate reset token
    reset_token = auth_service.generate_password_reset_token()
    token_hash = auth_service.hash_token(reset_token)

    # Create password reset token record
    expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

    password_reset = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        used=False
    )

    db.add(password_reset)
    db.commit()

    # In production, send email with reset link
    # For now, return token for testing
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token,  # Remove this in production!
        "expires_in_minutes": 60
    }


@router.post("/api/auth/reset-password", tags=["Authentication"])
def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using a reset token

    Token must be valid and not expired
    """
    # Validate new password strength
    is_valid, error_message = auth_service.validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Find all password reset tokens (we need to check the hash)
    reset_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).all()

    # Find matching token
    matching_token = None
    for token_record in reset_tokens:
        if auth_service.verify_token_hash(request.token, token_record.token_hash):
            matching_token = token_record
            break

    if not matching_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Get user
    user = db.query(User).filter(User.id == matching_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.password_hash = auth_service.hash_password(request.new_password)

    # Mark token as used
    matching_token.used = True
    matching_token.used_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Password reset successful",
        "user_id": user.id
    }
