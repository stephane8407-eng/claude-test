from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.village import Village

router = APIRouter(prefix="/api/villages", tags=["villages"])

@router.get("/", response_model=List[dict])
def list_villages(
    country: str = None,
    subscription_tier: str = None,
    db: Session = Depends(get_db)
):
    """
    List all villages with optional filters

    Filters:
    - country: FR, UK, BE
    - subscription_tier: free, partner, flagship
    """
    query = db.query(Village)

    if country:
        query = query.filter(Village.country == country)
    if subscription_tier:
        query = query.filter(Village.subscription_tier == subscription_tier)

    villages = query.order_by(Village.name).all()
    return [v.to_dict() for v in villages]

@router.get("/{slug}", response_model=dict)
def get_village(slug: str, db: Session = Depends(get_db)):
    """Get single village by slug"""
    village = db.query(Village).filter(Village.slug == slug).first()

    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")

    return village.to_dict()

@router.get("/{slug}/conflicts", response_model=List[dict])
def get_village_conflicts(slug: str, db: Session = Depends(get_db)):
    """Get all conflicts for a village"""
    from app.models.local_conflict import LocalConflict

    village = db.query(Village).filter(Village.slug == slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")

    conflicts = db.query(LocalConflict)\
        .filter(LocalConflict.village_id == village.id)\
        .order_by(LocalConflict.date.desc())\
        .all()

    return [c.to_dict() for c in conflicts]

@router.get("/{slug}/stats", response_model=dict)
def get_village_stats(slug: str, db: Session = Depends(get_db)):
    """Get statistics for a village"""
    from app.models.local_conflict import LocalConflict
    from sqlalchemy import func as sql_func

    village = db.query(Village).filter(Village.slug == slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{slug}' not found")

    # Count conflicts by period
    conflict_count = db.query(sql_func.count(LocalConflict.id))\
        .filter(LocalConflict.village_id == village.id)\
        .scalar()

    return {
        'village': village.to_dict(),
        'total_conflicts': conflict_count,
        'has_identity_themes': village.identity_themes is not None
    }
