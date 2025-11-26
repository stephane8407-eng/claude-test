"""
Permission decorators and middleware for authorization
"""
from functools import wraps
from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.models.village import Village
from app.models.role import Role
from app.models.permission import Permission


class PermissionChecker:
    """Dependency for checking permissions"""

    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Check if user has required permissions"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # System admins have all permissions
        if current_user.role_obj and current_user.role_obj.name == 'admin':
            return current_user

        # Get user's role with permissions
        if not current_user.role_obj:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )

        # Check if user has all required permissions
        user_permissions = {p.name for p in current_user.role_obj.permissions}
        missing_permissions = set(self.required_permissions) - user_permissions

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing_permissions)}"
            )

        return current_user


class RoleChecker:
    """Dependency for checking roles"""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        """Check if user has one of the allowed roles"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        if not current_user.role_obj:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )

        if current_user.role_obj.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(self.allowed_roles)}"
            )

        return current_user


class VillageOwnerChecker:
    """Dependency for checking village ownership"""

    def __init__(self, village_param: str = "village_slug"):
        self.village_param = village_param

    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        village_slug: Optional[str] = None
    ):
        """Check if user owns or has access to the village"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # System admins can access any village
        if current_user.role_obj and current_user.role_obj.name == 'admin':
            return current_user

        # If no village specified, just return user
        if not village_slug:
            return current_user

        # Get the village
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village not found"
            )

        # Check if user's village_id matches
        if current_user.village_id != village.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this village"
            )

        return current_user


class SubscriptionTierChecker:
    """Dependency for checking subscription tier"""

    def __init__(self, required_tier: str):
        self.tier_hierarchy = {
            'free': 0,
            'partner': 1,
            'enterprise': 2
        }
        self.required_tier = required_tier

    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
        village_slug: Optional[str] = None
    ):
        """Check if user's village has required subscription tier"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # System admins bypass tier checks
        if current_user.role_obj and current_user.role_obj.name == 'admin':
            return current_user

        # Get the village (from user or parameter)
        village = None
        if village_slug:
            village = db.query(Village).filter(Village.slug == village_slug).first()
        elif current_user.village_id:
            village = db.query(Village).filter(Village.id == current_user.village_id).first()

        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village not found"
            )

        # Check tier
        current_tier = village.subscription_tier or 'free'
        required_tier_level = self.tier_hierarchy.get(self.required_tier, 0)
        current_tier_level = self.tier_hierarchy.get(current_tier, 0)

        if current_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires {self.required_tier} subscription tier or higher"
            )

        return current_user


# Convenience functions for common checks
def require_auth():
    """Require authentication (shorthand for get_current_active_user)"""
    return Depends(get_current_active_user)


def require_role(*roles: str):
    """Require one of the specified roles

    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    return Depends(RoleChecker(list(roles)))


def require_permission(*permissions: str):
    """Require all specified permissions

    Usage:
        @app.post("/pois", dependencies=[Depends(require_permission("can_add_poi"))])
    """
    return Depends(PermissionChecker(list(permissions)))


def require_village_owner(village_param: str = "village_slug"):
    """Require user to own the village

    Usage:
        @app.put("/villages/{village_slug}", dependencies=[Depends(require_village_owner())])
    """
    return Depends(VillageOwnerChecker(village_param))


def require_tier(tier: str):
    """Require minimum subscription tier

    Usage:
        @app.get("/analytics", dependencies=[Depends(require_tier("partner"))])
    """
    return Depends(SubscriptionTierChecker(tier))


# Helper function to check permissions programmatically
def has_permission(user: User, permission_name: str) -> bool:
    """Check if user has a specific permission"""
    if not user or not user.role_obj:
        return False

    # System admins have all permissions
    if user.role_obj.name == 'admin':
        return True

    return user.role_obj.has_permission(permission_name)


def has_role(user: User, role_name: str) -> bool:
    """Check if user has a specific role"""
    if not user or not user.role_obj:
        return False

    return user.role_obj.name == role_name


def can_access_village(user: User, village: Village) -> bool:
    """Check if user can access a village"""
    if not user or not village:
        return False

    # System admins can access any village
    if user.role_obj and user.role_obj.name == 'admin':
        return True

    # Check if user's village_id matches
    return user.village_id == village.id


def meets_tier_requirement(village: Village, required_tier: str) -> bool:
    """Check if village meets tier requirement"""
    tier_hierarchy = {
        'free': 0,
        'partner': 1,
        'enterprise': 2
    }

    if not village:
        return False

    current_tier = village.subscription_tier or 'free'
    required_tier_level = tier_hierarchy.get(required_tier, 0)
    current_tier_level = tier_hierarchy.get(current_tier, 0)

    return current_tier_level >= required_tier_level
