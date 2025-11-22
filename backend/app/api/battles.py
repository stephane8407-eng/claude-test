"""
Battle API endpoints - Enhanced with spatial search, full-text search, and caching
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from functools import lru_cache
import json

from app.database import get_db
from app.models import Battle

router = APIRouter(prefix="/api/battles", tags=["battles"])


@router.get("/")
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

    Returns paginated response with metadata.

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
    Get comprehensive statistics about battles in the database.

    Returns:
    - Total battle count
    - Count by war period
    - Count by country
    - Count by significance
    - Date range covered (earliest to latest)
    - Total estimated casualties
    - Average casualties per battle
    """
    total_battles = db.query(func.count(Battle.id)).scalar()

    # Count by war period
    by_period = db.query(
        Battle.war_period,
        func.count(Battle.id).label('count')
    ).group_by(Battle.war_period).order_by(func.count(Battle.id).desc()).all()

    # Count by country
    by_country = db.query(
        Battle.country,
        func.count(Battle.id).label('count')
    ).group_by(Battle.country).order_by(func.count(Battle.id).desc()).all()

    # Count by significance
    by_significance = db.query(
        Battle.significance,
        func.count(Battle.id).label('count')
    ).group_by(Battle.significance).order_by(func.count(Battle.id).desc()).all()

    # Date range covered
    date_range = db.query(
        func.min(Battle.start_date).label('earliest'),
        func.max(Battle.end_date).label('latest')
    ).first()

    # Casualty statistics
    casualty_stats = db.query(
        func.sum(Battle.casualties_estimated).label('total'),
        func.avg(Battle.casualties_estimated).label('average'),
        func.max(Battle.casualties_estimated).label('max'),
        func.count(Battle.casualties_estimated).label('battles_with_data')
    ).first()

    return {
        "total_battles": total_battles,
        "by_war_period": [{"war_period": period or "Unknown", "count": count} for period, count in by_period],
        "by_country": [{"country": country or "Unknown", "count": count} for country, count in by_country],
        "by_significance": [{"significance": sig or "Unknown", "count": count} for sig, count in by_significance],
        "date_range": {
            "earliest": date_range.earliest.isoformat() if date_range.earliest else None,
            "latest": date_range.latest.isoformat() if date_range.latest else None,
            "span_years": (date_range.latest.year - date_range.earliest.year) if (date_range.earliest and date_range.latest) else None
        },
        "casualties": {
            "total_estimated": int(casualty_stats.total) if casualty_stats.total else 0,
            "average_per_battle": round(float(casualty_stats.average), 1) if casualty_stats.average else 0,
            "highest_single_battle": int(casualty_stats.max) if casualty_stats.max else 0,
            "battles_with_casualty_data": casualty_stats.battles_with_data
        }
    }


@router.get("/spatial/bbox", response_model=dict)
async def get_battles_in_bounding_box(
    min_lat: float = Query(..., description="Minimum latitude (south)", ge=-90, le=90),
    min_lng: float = Query(..., description="Minimum longitude (west)", ge=-180, le=180),
    max_lat: float = Query(..., description="Maximum latitude (north)", ge=-90, le=90),
    max_lng: float = Query(..., description="Maximum longitude (east)", ge=-180, le=180),
    war_period: Optional[str] = Query(None, description="Filter by war period"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Find all battles within a bounding box (rectangle on map).

    Perfect for: "Show me all WW1 battles visible in current map viewport"

    Parameters:
    - min_lat, min_lng: Southwest corner of bounding box
    - max_lat, max_lng: Northeast corner of bounding box
    - war_period: Optional filter by war period
    - limit: Max results (default 100)

    Example:
    ```
    # Battles in northern France
    GET /api/battles/spatial/bbox?min_lat=48.5&min_lng=1.5&max_lat=51.0&max_lng=4.5
    ```

    Returns battles sorted by significance (major first).
    """
    # Validate bounding box
    if min_lat >= max_lat:
        raise HTTPException(status_code=400, detail="min_lat must be less than max_lat")
    if min_lng >= max_lng:
        raise HTTPException(status_code=400, detail="min_lng must be less than max_lng")

    # Build query
    query = db.query(Battle).filter(
        and_(
            Battle.latitude >= min_lat,
            Battle.latitude <= max_lat,
            Battle.longitude >= min_lng,
            Battle.longitude <= max_lng
        )
    )

    # Apply optional filters
    if war_period:
        query = query.filter(Battle.war_period == war_period)

    # Order by significance (major > moderate > minor)
    significance_order = func.case(
        (Battle.significance == 'major', 1),
        (Battle.significance == 'moderate', 2),
        (Battle.significance == 'minor', 3),
        else_=4
    )
    query = query.order_by(significance_order, Battle.name)

    total = query.count()
    battles = query.limit(limit).all()

    return {
        "total": total,
        "returned": len(battles),
        "bounding_box": {
            "min_lat": min_lat,
            "min_lng": min_lng,
            "max_lat": max_lat,
            "max_lng": max_lng
        },
        "battles": [battle.to_dict() for battle in battles]
    }


@router.post("/spatial/route", response_model=dict)
async def get_battles_along_route(
    route: Dict[str, Any] = Body(
        ...,
        example={
            "coordinates": [
                [2.3522, 48.8566],  # Paris [lng, lat]
                [4.8357, 45.7640]   # Lyon [lng, lat]
            ],
            "radius_km": 30,
            "war_period": "WW2"
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Find all battles along a route (polyline) within a given radius.

    Perfect for: "Show me all WW1 battles within 50km of my road trip route"

    Request body:
    ```json
    {
        "coordinates": [[lng1, lat1], [lng2, lat2], ...],
        "radius_km": 50,
        "war_period": "WW1"  // Optional
    }
    ```

    Uses PostGIS ST_LineString and ST_Buffer for efficient spatial query.
    Returns battles sorted by distance from route (closest first).
    """
    # Validate input
    coords = route.get("coordinates", [])
    if len(coords) < 2:
        raise HTTPException(status_code=400, detail="Route must have at least 2 coordinates")

    radius_km = route.get("radius_km", 30)
    if radius_km < 1 or radius_km > 200:
        raise HTTPException(status_code=400, detail="radius_km must be between 1 and 200")

    war_period = route.get("war_period")

    # Convert coordinates to PostGIS LINESTRING format
    # Format: LINESTRING(lng1 lat1, lng2 lat2, ...)
    linestring_coords = ", ".join([f"{lng} {lat}" for lng, lat in coords])
    linestring_wkt = f"LINESTRING({linestring_coords})"

    # Query battles near the route using ST_DWithin
    # This finds all points within radius_km of any point on the route
    query = text("""
        SELECT
            b.*,
            ROUND(
                ST_Distance(
                    ST_GeomFromText(:linestring, 4326)::geography,
                    ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography
                ) / 1000, 2
            ) as distance_km
        FROM battles b
        WHERE ST_DWithin(
            ST_GeomFromText(:linestring, 4326)::geography,
            ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography,
            :radius_m
        )
        """ + (" AND b.war_period = :war_period" if war_period else "") + """
        ORDER BY distance_km
        LIMIT 100
    """)

    params = {
        "linestring": linestring_wkt,
        "radius_m": radius_km * 1000
    }
    if war_period:
        params["war_period"] = war_period

    result = db.execute(query, params).fetchall()

    # Convert result to list of dicts
    battles = []
    for row in result:
        battle_dict = {
            "id": row[0],
            "name": row[1],
            "war_period": row[2],
            "start_date": row[3].isoformat() if row[3] else None,
            "end_date": row[4].isoformat() if row[4] else None,
            "latitude": float(row[5]),
            "longitude": float(row[6]),
            "country": row[7],
            "sides_involved": row[8],
            "outcome": row[9],
            "significance": row[10],
            "casualties_estimated": row[11],
            "sources": row[12],
            "distance_km": float(row[-1])  # Last column is distance
        }
        battles.append(battle_dict)

    return {
        "total": len(battles),
        "route": {
            "coordinates": coords,
            "radius_km": radius_km,
            "total_length_km": None  # TODO: Calculate route length
        },
        "battles": battles
    }


@router.get("/search/fulltext", response_model=dict)
async def fulltext_search_battles(
    q: str = Query(..., min_length=2, description="Search query"),
    search_fields: str = Query(
        "name,outcome,sides",
        description="Comma-separated fields to search: name,outcome,sides,all"
    ),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    Full-text search across battle data.

    Search in:
    - name: Battle names
    - outcome: Battle outcomes
    - sides: Participating sides (sides_involved array)
    - all: Search all fields

    Examples:
    ```
    # Find battles with "Somme" in name
    GET /api/battles/search/fulltext?q=Somme&search_fields=name

    # Find battles involving "British" or "German"
    GET /api/battles/search/fulltext?q=British&search_fields=sides

    # Search everything
    GET /api/battles/search/fulltext?q=victory&search_fields=all
    ```

    Returns relevance-scored results (exact matches first, then partial).
    """
    search_term = f"%{q}%"
    fields = [f.strip().lower() for f in search_fields.split(",")]

    # Build search conditions
    conditions = []

    if "name" in fields or "all" in fields:
        conditions.append(Battle.name.ilike(search_term))

    if "outcome" in fields or "all" in fields:
        conditions.append(Battle.outcome.ilike(search_term))

    if "sides" in fields or "all" in fields:
        # Search in array field - PostgreSQL array search
        # Using ANY to search within array elements
        conditions.append(
            text(f"EXISTS (SELECT 1 FROM unnest(sides_involved) AS side WHERE side ILIKE :search_term)")
        )

    if not conditions:
        raise HTTPException(status_code=400, detail="Invalid search_fields. Use: name, outcome, sides, or all")

    # Execute query
    if "sides" in fields or "all" in fields:
        # Need to use raw SQL for array search
        query = db.query(Battle).filter(or_(*conditions[:2]) if len(conditions) > 2 else or_(*conditions))
        query = query.params(search_term=search_term)
    else:
        query = db.query(Battle).filter(or_(*conditions))

    battles = query.limit(limit).all()

    # Calculate relevance scores (simple: exact match = 10, contains = 5)
    results = []
    for battle in battles:
        score = 0
        q_lower = q.lower()

        # Score name matches
        if battle.name and q_lower in battle.name.lower():
            score += 10 if q_lower == battle.name.lower() else 5

        # Score outcome matches
        if battle.outcome and q_lower in battle.outcome.lower():
            score += 5

        # Score sides matches
        if battle.sides_involved:
            for side in battle.sides_involved:
                if side and q_lower in side.lower():
                    score += 3

        battle_dict = battle.to_dict()
        battle_dict["relevance_score"] = score
        results.append(battle_dict)

    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)

    return {
        "query": q,
        "search_fields": fields,
        "total": len(results),
        "battles": results
    }
