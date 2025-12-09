"""
Village Identity API Endpoints

Handles saving and retrieving AI-generated village identities.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Village, VillageIdentity
from app.middleware.auth import get_current_user, require_village_admin

router = APIRouter(prefix="/api/villages", tags=["village_identity"])


# =====================================
# PYDANTIC SCHEMAS
# =====================================

class ThemeSchema(BaseModel):
    """Schema for a theme object"""
    theme_name: str
    confidence_score: Optional[float] = None
    theme_story: Optional[str] = None
    project_ideas: Optional[List[Dict[str, Any]]] = []


class ProjectSchema(BaseModel):
    """Schema for a project object"""
    title: str
    short_description: Optional[str] = ""
    themes: Optional[List[str]] = []
    status: Optional[str] = "idea"
    source: Optional[str] = "ai_suggested"


class SaveIdentityRequest(BaseModel):
    """Request body for saving village identity"""
    summary_identity: str
    long_identity: str
    live_here_summary: str
    themes: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []


class IdentityResponse(BaseModel):
    """Response schema for village identity"""
    id: int
    village_id: int
    identity_summary: str
    identity_narrative: str
    live_here_summary: str
    selected_themes: List[Dict[str, Any]]
    selected_projects: List[Dict[str, Any]]
    is_published: bool
    published_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# =====================================
# SAVE IDENTITY (PUT)
# =====================================

@router.put("/{village_slug}/identity")
def save_village_identity(
    village_slug: str,
    request: SaveIdentityRequest,
    current_user: User = Depends(require_village_admin),
    db: Session = Depends(get_db)
):
    """
    Save and publish village identity.

    Requires village_admin role.
    User must be the admin for this specific village.
    """
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Village '{village_slug}' not found"
        )

    # Verify user has permission for this village
    # System admins can edit any village, village admins only their own
    if current_user.role != "admin" and current_user.village_id != village.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to save identity for this village"
        )

    now = datetime.utcnow()

    # Check if identity already exists
    existing_identity = db.query(VillageIdentity).filter(
        VillageIdentity.village_id == village.id
    ).first()

    if existing_identity:
        # Update existing identity
        existing_identity.identity_summary = request.summary_identity
        existing_identity.identity_narrative = request.long_identity
        existing_identity.live_here_summary = request.live_here_summary
        existing_identity.selected_themes = request.themes
        existing_identity.selected_projects = request.projects
        existing_identity.is_published = True
        existing_identity.published_at = now
        existing_identity.updated_at = now

        db.commit()
        db.refresh(existing_identity)

        # Also update the village table for quick access
        _update_village_identity_fields(db, village, request)

        return {
            "success": True,
            "message": "Identity updated and published successfully",
            "identity_id": existing_identity.id
        }

    else:
        # Create new identity
        new_identity = VillageIdentity(
            village_id=village.id,
            identity_summary=request.summary_identity,
            identity_narrative=request.long_identity,
            live_here_summary=request.live_here_summary,
            selected_themes=request.themes,
            selected_projects=request.projects,
            is_published=True,
            published_at=now
        )

        db.add(new_identity)
        db.commit()
        db.refresh(new_identity)

        # Also update the village table for quick access
        _update_village_identity_fields(db, village, request)

        return {
            "success": True,
            "message": "Identity saved and published successfully",
            "identity_id": new_identity.id
        }


def _update_village_identity_fields(db: Session, village: Village, request: SaveIdentityRequest):
    """
    Update the identity fields on the Village model for quick access.
    These fields are used for public display without needing to join tables.
    """
    village.summary_identity = request.summary_identity
    village.long_identity = request.long_identity
    village.live_here_summary = request.live_here_summary

    # Extract theme names for the themes array
    theme_names = [t.get('theme_name', '') for t in request.themes if t.get('theme_name')]
    village.themes = theme_names

    db.commit()


# =====================================
# GET IDENTITY
# =====================================

@router.get("/{village_slug}/identity")
def get_village_identity(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get published village identity.

    Public endpoint - no authentication required.
    """
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Village '{village_slug}' not found"
        )

    # Get identity
    identity = db.query(VillageIdentity).filter(
        VillageIdentity.village_id == village.id,
        VillageIdentity.is_published == True
    ).first()

    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No published identity found for village '{village_slug}'"
        )

    return identity.to_dict()


# =====================================
# DELETE IDENTITY (Admin only)
# =====================================

@router.delete("/{village_slug}/identity")
def delete_village_identity(
    village_slug: str,
    current_user: User = Depends(require_village_admin),
    db: Session = Depends(get_db)
):
    """
    Delete village identity.

    Requires village_admin role for the specific village.
    """
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Village '{village_slug}' not found"
        )

    # Verify user has permission
    if current_user.role != "admin" and current_user.village_id != village.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete identity for this village"
        )

    # Get and delete identity
    identity = db.query(VillageIdentity).filter(
        VillageIdentity.village_id == village.id
    ).first()

    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No identity found for village '{village_slug}'"
        )

    db.delete(identity)

    # Clear village identity fields
    village.summary_identity = None
    village.long_identity = None
    village.live_here_summary = None
    village.themes = None

    db.commit()

    return {
        "success": True,
        "message": "Identity deleted successfully"
    }
