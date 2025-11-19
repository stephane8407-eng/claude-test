"""
Battle API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.database import get_db
from app.models import Battle

router = APIRouter(prefix="/api/battles", tags=["battles"])


@router.get("/", response_model=List[dict])
async def list_battles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    war_period: Optional[str] = Query(None, description="Filter by war period (WW1, WW2, etc.)"),
    country: Optional[str] = Query(None, description="Filter by country (FR, UK, BE)"),
    significance: Optional[str] = Query(None, description="Filter by significance (minor, moderate, major)"),
    db: Session = Depends(get_db)
):
    """
    List all battles with optional filtering.

    Query parameters:
    - skip: Pagination offset
    - limit: Max results (default 100, max 1000)
    - war_period: Filter by period (e.g., "WW1", "WW2", "Napoleonic")
    - country: Filter by country code (FR, UK, BE)
    - significance: Filter by significance level
    """
    query = db.query(Battle)

    # Apply filters
    if war_period:
        query = query.filter(Battle.war_period == war_period)
    if country:
        query = query.filter(Battle.country == country)
    if significance:
        query = query.filter(Battle.significance == significance)

    # Get total count for pagination metadata
    total = query.count()

    # Apply pagination
    battles = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [battle.to_dict() for battle in battles]
    }


@router.get("/{battle_id}", response_model=dict)
async def get_battle(battle_id: int, db: Session = Depends(get_db)):
    """
    Get a specific battle by ID.
    """
    battle = db.query(Battle).filter(Battle.id == battle_id).first()

    if not battle:
        raise HTTPException(status_code=404, detail=f"Battle {battle_id} not found")

    return battle.to_dict()


@router.get("/nearby/", response_model=List[dict])
async def get_nearby_battles(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, ge=1, le=500, description="Search radius in km"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Find battles near a specific location within a given radius.

    Uses PostGIS for efficient spatial queries.
    Returns battles sorted by distance (nearest first).
    """
    # PostGIS query to find battles within radius
    # ST_DWithin uses geography type for accurate distance in meters
    battles = db.query(
        Battle,
        func.round(
            func.ST_Distance(
                func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
                func.ST_SetSRID(func.ST_MakePoint(Battle.longitude, Battle.latitude), 4326).cast(type_=func.geography)
            ) / 1000, 2
        ).label('distance_km')
    ).filter(
        func.ST_DWithin(
            func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
            func.ST_SetSRID(func.ST_MakePoint(Battle.longitude, Battle.latitude), 4326).cast(type_=func.geography),
            radius_km * 1000  # Convert km to meters
        )
    ).order_by('distance_km').limit(limit).all()

    return [
        {
            **battle.to_dict(),
            "distance_km": float(distance)
        }
        for battle, distance in battles
    ]


@router.get("/search/", response_model=List[dict])
async def search_battles(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search battles by name or outcome.

    Performs case-insensitive partial matching on battle name and outcome.
    """
    search_term = f"%{q}%"

    battles = db.query(Battle).filter(
        or_(
            Battle.name.ilike(search_term),
            Battle.outcome.ilike(search_term)
        )
    ).limit(limit).all()

    return [battle.to_dict() for battle in battles]


@router.get("/stats/summary", response_model=dict)
async def get_battle_statistics(db: Session = Depends(get_db)):
    """
    Get summary statistics about battles in the database.
    """
    total_battles = db.query(func.count(Battle.id)).scalar()

    # Count by war period
    by_period = db.query(
        Battle.war_period,
        func.count(Battle.id).label('count')
    ).group_by(Battle.war_period).all()

    # Count by country
    by_country = db.query(
        Battle.country,
        func.count(Battle.id).label('count')
    ).group_by(Battle.country).all()

    # Count by significance
    by_significance = db.query(
        Battle.significance,
        func.count(Battle.id).label('count')
    ).group_by(Battle.significance).all()

    return {
        "total_battles": total_battles,
        "by_war_period": [{"war_period": period, "count": count} for period, count in by_period],
        "by_country": [{"country": country, "count": count} for country, count in by_country],
        "by_significance": [{"significance": sig, "count": count} for sig, count in by_significance],
    }
