"""
Local Conflicts API endpoints - AI-scraped conflict events with Impact Today framework
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models import LocalConflict

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])


@router.get("/")
async def list_conflicts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    village_slug: Optional[str] = Query(None, description="Filter by village slug (chirac, manot, etc.)"),
    conflict_type: Optional[str] = Query(None, description="Filter by conflict type (battle, siege, skirmish, etc.)"),
    period: Optional[str] = Query(None, description="Filter by period (ancient, medieval, ww1, ww2, etc.)"),
    confidence_min: Optional[int] = Query(None, ge=0, le=100, description="Minimum confidence score"),
    confidence_max: Optional[int] = Query(None, ge=0, le=100, description="Maximum confidence score"),
    db: Session = Depends(get_db)
):
    """
    List all local conflicts with optional filtering.

    Returns paginated response with metadata.

    Query parameters:
    - skip: Pagination offset
    - limit: Max results (default 100, max 1000)
    - village_slug: Filter by village (chirac, manot, etc.)
    - conflict_type: Filter by type (battle, siege, skirmish, raid, occupation, bombardment)
    - period: Filter by historical period (ancient, medieval, renaissance, revolutionary, napoleonic, ww1, ww2, modern)
    - confidence_min: Minimum confidence score (0-100)
    - confidence_max: Maximum confidence score (0-100)
    """
    query = db.query(LocalConflict)

    # Apply village filter
    if village_slug:
        from app.models.village import Village
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if village:
            query = query.filter(LocalConflict.village_id == village.id)

    # Apply filters
    if conflict_type:
        query = query.filter(LocalConflict.conflict_type == conflict_type)
    if period:
        query = query.filter(LocalConflict.period == period)
    if confidence_min is not None:
        query = query.filter(LocalConflict.confidence_score >= confidence_min)
    if confidence_max is not None:
        query = query.filter(LocalConflict.confidence_score <= confidence_max)

    # Get total count for pagination metadata
    total = query.count()

    # Apply pagination and ordering (most recent/highest confidence first)
    conflicts = query.order_by(
        LocalConflict.confidence_score.desc(),
        LocalConflict.date.desc()
    ).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [conflict.to_dict() for conflict in conflicts]
    }


@router.get("/{conflict_id}")
async def get_conflict(conflict_id: int, db: Session = Depends(get_db)):
    """
    Get a specific conflict by ID.
    """
    conflict = db.query(LocalConflict).filter(LocalConflict.id == conflict_id).first()

    if not conflict:
        raise HTTPException(status_code=404, detail=f"Conflict {conflict_id} not found")

    return conflict.to_dict()


@router.get("/nearby/")
async def get_nearby_conflicts(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, ge=1, le=500, description="Search radius in km"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Find conflicts near a specific location within a given radius.

    Uses PostGIS for efficient spatial queries.
    Returns conflicts sorted by distance (nearest first).
    """
    # PostGIS query to find conflicts within radius
    conflicts = db.query(
        LocalConflict,
        func.round(
            func.ST_Distance(
                func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
                func.ST_SetSRID(func.ST_MakePoint(LocalConflict.longitude, LocalConflict.latitude), 4326).cast(type_=func.geography)
            ) / 1000, 2
        ).label('distance_km')
    ).filter(
        func.ST_DWithin(
            func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
            func.ST_SetSRID(func.ST_MakePoint(LocalConflict.longitude, LocalConflict.latitude), 4326).cast(type_=func.geography),
            radius_km * 1000  # Convert km to meters
        )
    ).order_by('distance_km').limit(limit).all()

    return [
        {
            **conflict.to_dict(),
            "distance_km": float(distance_km)
        }
        for conflict, distance_km in conflicts
    ]


@router.get("/stats/summary")
async def get_conflicts_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics about conflicts in the database.

    Returns counts by period, type, and confidence distribution.
    """
    # Count by period
    by_period = db.query(
        LocalConflict.period,
        func.count(LocalConflict.id).label('count')
    ).group_by(LocalConflict.period).all()

    # Count by conflict type
    by_type = db.query(
        LocalConflict.conflict_type,
        func.count(LocalConflict.id).label('count')
    ).group_by(LocalConflict.conflict_type).all()

    # Average confidence score
    avg_confidence = db.query(
        func.avg(LocalConflict.confidence_score)
    ).scalar()

    # Total count
    total = db.query(func.count(LocalConflict.id)).scalar()

    return {
        "total_conflicts": total,
        "average_confidence": round(float(avg_confidence), 1) if avg_confidence else 0,
        "by_period": {period: count for period, count in by_period},
        "by_type": {ctype: count for ctype, count in by_type}
    }
