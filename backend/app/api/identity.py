from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Village, IdentityCategory, IdentityTheme, VillageDataSnapshot

router = APIRouter()

# =====================================
# IDENTITY CATEGORY ENDPOINTS
# =====================================

@router.get("/api/identity/categories", tags=["Identity"])
def get_identity_categories(db: Session = Depends(get_db)):
    """Get all 6 identity categories"""
    categories = db.query(IdentityCategory).all()
    return [cat.to_dict() for cat in categories]

# =====================================
# IDENTITY THEME ENDPOINTS
# =====================================

@router.get("/api/villages/{village_slug}/identity", tags=["Identity"])
def get_village_identity_themes(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get all identity themes for a village"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    themes = db.query(IdentityTheme).filter(
        IdentityTheme.village_id == village.id
    ).order_by(IdentityTheme.display_order).all()

    return [theme.to_dict() for theme in themes]

@router.get("/api/villages/{village_slug}/identity/{theme_id}", tags=["Identity"])
def get_identity_theme_detail(
    village_slug: str,
    theme_id: int,
    db: Session = Depends(get_db)
):
    """Get details of a specific identity theme"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    theme = db.query(IdentityTheme).filter(
        IdentityTheme.id == theme_id,
        IdentityTheme.village_id == village.id  # Village isolation
    ).first()

    if not theme:
        raise HTTPException(status_code=404, detail="Identity theme not found")

    return theme.to_dict()

@router.get("/api/villages/{village_slug}/identity-summary", tags=["Identity"])
def get_village_identity_summary(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get summary of village identity (featured themes only)"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    featured_themes = db.query(IdentityTheme).filter(
        IdentityTheme.village_id == village.id,
        IdentityTheme.is_featured == True
    ).order_by(IdentityTheme.display_order).all()

    return {
        "village": village.to_dict(),
        "featured_themes": [theme.to_dict() for theme in featured_themes],
        "total_themes": db.query(IdentityTheme).filter(
            IdentityTheme.village_id == village.id
        ).count()
    }

# =====================================
# DATA SNAPSHOT ENDPOINT
# =====================================

@router.get("/api/villages/{village_slug}/data-snapshot", tags=["Identity"])
def get_village_data_snapshot(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get latest data snapshot for a village"""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    # Get most recent snapshot
    snapshot = db.query(VillageDataSnapshot).filter(
        VillageDataSnapshot.village_id == village.id
    ).order_by(VillageDataSnapshot.snapshot_date.desc()).first()

    if not snapshot:
        raise HTTPException(status_code=404, detail="No data snapshot found for this village")

    return snapshot.to_dict()
