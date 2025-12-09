from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.poi import POI
from app.models.poi_type import POIType
from app.models.village import Village

router = APIRouter(prefix="/api/pois", tags=["pois"])

@router.get("/types", response_model=List[dict])
def list_poi_types(db: Session = Depends(get_db)):
    """
    List all available POI types

    Returns all POI type definitions (shared across villages)
    """
    poi_types = db.query(POIType).order_by(POIType.category, POIType.name).all()
    return [pt.to_dict() for pt in poi_types]

@router.get("/", response_model=dict)
def list_pois(
    village_slug: Optional[str] = Query(None, description="Filter by village slug"),
    poi_type_id: Optional[int] = Query(None, description="Filter by POI type ID"),
    category: Optional[str] = Query(None, description="Filter by category (water, religious, heritage)"),
    is_public: Optional[bool] = Query(None, description="Filter by public visibility"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    List POIs with optional filters

    Query parameters:
    - village_slug: Filter by village (e.g., "chirac", "manot")
    - poi_type_id: Filter by POI type ID
    - category: Filter by category (water, religious, heritage, nature, infrastructure)
    - is_public: Filter by public visibility
    - limit: Max results (default 100)
    - offset: Pagination offset
    """
    query = db.query(POI)

    # Filter by village
    if village_slug:
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if village:
            query = query.filter(POI.village_id == village.id)

    # Filter by POI type
    if poi_type_id:
        query = query.filter(POI.poi_type_id == poi_type_id)

    # Filter by category
    if category:
        query = query.join(POIType).filter(POIType.category == category)

    # Filter by public visibility
    if is_public is not None:
        query = query.filter(POI.is_public == is_public)

    # Get total count
    total = query.count()

    # Apply pagination
    pois = query.order_by(POI.name).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": [poi.to_dict() for poi in pois]
    }

@router.get("/{poi_id}", response_model=dict)
def get_poi(poi_id: int, db: Session = Depends(get_db)):
    """
    Get a specific POI by ID

    Returns detailed information about a single POI
    """
    poi = db.query(POI).filter(POI.id == poi_id).first()

    if not poi:
        raise HTTPException(status_code=404, detail=f"POI {poi_id} not found")

    # Also include POI type info
    poi_type = db.query(POIType).filter(POIType.id == poi.poi_type_id).first()

    result = poi.to_dict()
    if poi_type:
        result['poi_type'] = poi_type.to_dict()

    return result

@router.get("/village/{village_slug}", response_model=dict)
def get_village_pois(
    village_slug: str,
    poi_type_id: Optional[int] = Query(None, description="Filter by POI type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get all POIs for a specific village

    Returns all POIs belonging to the specified village with optional filters
    """
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{village_slug}' not found")

    query = db.query(POI).filter(POI.village_id == village.id)

    # Apply filters
    if poi_type_id:
        query = query.filter(POI.poi_type_id == poi_type_id)

    if category:
        query = query.join(POIType).filter(POIType.category == category)

    pois = query.order_by(POI.name).all()

    # Group by POI type for easier frontend consumption
    pois_by_type = {}
    for poi in pois:
        poi_type = db.query(POIType).filter(POIType.id == poi.poi_type_id).first()
        type_name = poi_type.name if poi_type else "unknown"

        if type_name not in pois_by_type:
            pois_by_type[type_name] = {
                'type': poi_type.to_dict() if poi_type else None,
                'pois': []
            }
        pois_by_type[type_name]['pois'].append(poi.to_dict())

    return {
        'village': village.to_dict(),
        'total_pois': len(pois),
        'pois_by_type': pois_by_type
    }

@router.get("/village/{village_slug}/stats", response_model=dict)
def get_village_poi_stats(village_slug: str, db: Session = Depends(get_db)):
    """
    Get POI statistics for a village

    Returns counts by type, category, and other metrics
    """
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{village_slug}' not found")

    # Count by POI type
    by_type = db.query(
        POIType.name,
        func.count(POI.id).label('count')
    ).join(POI).filter(POI.village_id == village.id)\
     .group_by(POIType.name).all()

    # Count by category
    by_category = db.query(
        POIType.category,
        func.count(POI.id).label('count')
    ).join(POI).filter(POI.village_id == village.id)\
     .group_by(POIType.category).all()

    # Total count
    total = db.query(func.count(POI.id)).filter(POI.village_id == village.id).scalar()

    # Public vs private
    public_count = db.query(func.count(POI.id))\
        .filter(POI.village_id == village.id, POI.is_public == True).scalar()

    return {
        'village': village.to_dict(),
        'total_pois': total,
        'public_pois': public_count,
        'private_pois': total - public_count,
        'by_type': {name: count for name, count in by_type},
        'by_category': {category: count for category, count in by_category}
    }
