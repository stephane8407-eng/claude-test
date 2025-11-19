"""
Place API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from typing import List, Optional
from app.database import get_db
from app.models import Place, PlaceContext, Battle

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("/", response_model=List[dict])
async def list_places(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    country: Optional[str] = Query(None, description="Filter by country (FR, UK, BE)"),
    depth_level: Optional[str] = Query(None, description="Filter by depth (light, partner, flagship)"),
    db: Session = Depends(get_db)
):
    """
    List all places with optional filtering.

    Query parameters:
    - skip: Pagination offset
    - limit: Max results (default 100, max 1000)
    - country: Filter by country code (FR, UK, BE)
    - depth_level: Filter by content depth (light, partner, flagship)
    """
    query = db.query(Place)

    # Apply filters
    if country:
        query = query.filter(Place.country == country)
    if depth_level:
        query = query.filter(Place.depth_level == depth_level)

    # Get total count
    total = query.count()

    # Apply pagination
    places = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": [place.to_dict() for place in places]
    }


@router.get("/{place_id}", response_model=dict)
async def get_place(
    place_id: int,
    include_context: bool = Query(False, description="Include AI-generated context"),
    db: Session = Depends(get_db)
):
    """
    Get a specific place by ID.

    Set include_context=true to get AI-generated intelligence.
    """
    place = db.query(Place).filter(Place.id == place_id).first()

    if not place:
        raise HTTPException(status_code=404, detail=f"Place {place_id} not found")

    return place.to_dict(include_context=include_context)


@router.get("/{place_id}/context", response_model=dict)
async def get_place_context(
    place_id: int,
    include_raw: bool = Query(False, description="Include raw AI scraper JSON (260K+ chars)"),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated context/intelligence for a specific place.

    This includes:
    - AI summary (2-3 paragraphs)
    - Key historical events
    - Military units mentioned
    - Legends and folklore
    - Impact on the place today
    - Confidence score (0-100)

    Set include_raw=true to get the full scraper output (260K+ chars).
    """
    context = db.query(PlaceContext).filter(PlaceContext.place_id == place_id).first()

    if not context:
        raise HTTPException(status_code=404, detail=f"No context found for place {place_id}")

    return context.to_dict(include_raw=include_raw)


@router.get("/{place_id}/nearby-battles", response_model=List[dict])
async def get_place_nearby_battles(
    place_id: int,
    radius_km: float = Query(50, ge=1, le=500, description="Search radius in km"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Find battles near this place using the battles_near_place() database function.

    Returns battles within radius_km, sorted by distance (nearest first).
    """
    place = db.query(Place).filter(Place.id == place_id).first()

    if not place:
        raise HTTPException(status_code=404, detail=f"Place {place_id} not found")

    # Use the database function we created in the schema
    result = db.execute(
        text("SELECT * FROM battles_near_place(:place_id, :radius_km) LIMIT :limit"),
        {"place_id": place_id, "radius_km": radius_km, "limit": limit}
    ).fetchall()

    return [
        {
            "battle_id": row[0],
            "battle_name": row[1],
            "distance_km": float(row[2]),
            "war_period": row[3]
        }
        for row in result
    ]


@router.get("/nearby/", response_model=List[dict])
async def get_nearby_places(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(20, ge=1, le=200, description="Search radius in km"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Find places near a specific location within a given radius.

    Uses PostGIS for efficient spatial queries.
    Returns places sorted by distance (nearest first).
    """
    places = db.query(
        Place,
        func.round(
            func.ST_Distance(
                func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
                func.ST_SetSRID(func.ST_MakePoint(Place.centroid_lng, Place.centroid_lat), 4326).cast(type_=func.geography)
            ) / 1000, 2
        ).label('distance_km')
    ).filter(
        func.ST_DWithin(
            func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(type_=func.geography),
            func.ST_SetSRID(func.ST_MakePoint(Place.centroid_lng, Place.centroid_lat), 4326).cast(type_=func.geography),
            radius_km * 1000  # Convert km to meters
        )
    ).order_by('distance_km').limit(limit).all()

    return [
        {
            **place.to_dict(),
            "distance_km": float(distance)
        }
        for place, distance in places
    ]


@router.get("/search/", response_model=List[dict])
async def search_places(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Search places by name or admin code.

    Performs case-insensitive partial matching.
    """
    search_term = f"%{q}%"

    places = db.query(Place).filter(
        or_(
            Place.name.ilike(search_term),
            Place.admin_code.ilike(search_term)
        )
    ).limit(limit).all()

    return [place.to_dict() for place in places]


@router.get("/stats/summary", response_model=dict)
async def get_place_statistics(db: Session = Depends(get_db)):
    """
    Get summary statistics about places in the database.
    """
    total_places = db.query(func.count(Place.id)).scalar()
    total_with_context = db.query(func.count(PlaceContext.id)).scalar()

    # Count by country
    by_country = db.query(
        Place.country,
        func.count(Place.id).label('count')
    ).group_by(Place.country).all()

    # Count by depth level
    by_depth = db.query(
        Place.depth_level,
        func.count(Place.id).label('count')
    ).group_by(Place.depth_level).all()

    # Average confidence score for places with AI context
    avg_confidence = db.query(
        func.avg(PlaceContext.confidence_score)
    ).scalar()

    return {
        "total_places": total_places,
        "total_with_context": total_with_context,
        "by_country": [{"country": country, "count": count} for country, count in by_country],
        "by_depth_level": [{"depth_level": depth, "count": count} for depth, count in by_depth],
        "average_confidence_score": round(float(avg_confidence), 1) if avg_confidence else None,
    }
