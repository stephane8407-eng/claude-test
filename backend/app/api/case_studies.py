"""
Case Studies API - CRUD endpoints + similarity search for RAG context
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.revival_case_study import RevivalCaseStudy


router = APIRouter(prefix="/api/case-studies", tags=["case-studies"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class CaseStudyCreate(BaseModel):
    village_name: str
    country: str
    region: Optional[str] = None
    population_before: Optional[int] = None
    population_after: Optional[int] = None
    population_band: Optional[str] = None
    revival_type: Optional[str] = None
    strategy: str
    key_projects: Optional[List[str]] = None
    outcomes: str
    lessons_learned: Optional[str] = None
    timeline_years: Optional[int] = None
    themes: Optional[List[str]] = None
    geography_tags: Optional[List[str]] = None
    funding_sources: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class CaseStudyUpdate(BaseModel):
    village_name: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    population_before: Optional[int] = None
    population_after: Optional[int] = None
    population_band: Optional[str] = None
    revival_type: Optional[str] = None
    strategy: Optional[str] = None
    key_projects: Optional[List[str]] = None
    outcomes: Optional[str] = None
    lessons_learned: Optional[str] = None
    timeline_years: Optional[int] = None
    themes: Optional[List[str]] = None
    geography_tags: Optional[List[str]] = None
    funding_sources: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class SimilaritySearchRequest(BaseModel):
    population: Optional[int] = None
    themes: Optional[List[str]] = None
    geography: Optional[List[str]] = None
    limit: int = 5


# ============================================================================
# Public Endpoints
# ============================================================================

@router.get("/")
def list_case_studies(
    country: Optional[str] = Query(None, description="Filter by country"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    geography: Optional[str] = Query(None, description="Filter by geography tag"),
    population_band: Optional[str] = Query(None, description="Filter by population band"),
    revival_type: Optional[str] = Query(None, description="Filter by revival type"),
    search: Optional[str] = Query(None, description="Search in village name and strategy"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all case studies with optional filters.

    - **country**: Filter by country (e.g., 'France', 'Spain')
    - **theme**: Filter by theme (e.g., 'heritage', 'ecology')
    - **geography**: Filter by geography tag (e.g., 'mountains', 'coast')
    - **population_band**: Filter by population band (e.g., 'under_100', '500_1000')
    - **revival_type**: Filter by revival type (e.g., 'eco_village', 'artisan_hub')
    - **search**: Search in village name and strategy
    """
    query = db.query(RevivalCaseStudy)

    if country:
        query = query.filter(RevivalCaseStudy.country == country)

    if theme:
        query = query.filter(RevivalCaseStudy.themes.contains([theme]))

    if geography:
        query = query.filter(RevivalCaseStudy.geography_tags.contains([geography]))

    if population_band:
        query = query.filter(RevivalCaseStudy.population_band == population_band)

    if revival_type:
        query = query.filter(RevivalCaseStudy.revival_type == revival_type)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                RevivalCaseStudy.village_name.ilike(search_term),
                RevivalCaseStudy.strategy.ilike(search_term)
            )
        )

    total = query.count()
    case_studies = query.order_by(RevivalCaseStudy.village_name).offset(offset).limit(limit).all()

    return {
        "results": [cs.to_dict() for cs in case_studies],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/filters")
def get_case_study_filters(db: Session = Depends(get_db)):
    """
    Get available filter options for case studies.

    Returns distinct values for countries, themes, geography tags, population bands, and revival types.
    """
    # Get distinct countries
    countries = db.query(RevivalCaseStudy.country).distinct().all()
    countries = sorted([c[0] for c in countries if c[0]])

    # Get distinct population bands
    pop_bands = db.query(RevivalCaseStudy.population_band).distinct().all()
    pop_bands = sorted([p[0] for p in pop_bands if p[0]])

    # Get distinct revival types
    revival_types = db.query(RevivalCaseStudy.revival_type).distinct().all()
    revival_types = sorted([r[0] for r in revival_types if r[0]])

    # Get all themes (from arrays)
    all_case_studies = db.query(RevivalCaseStudy).all()
    themes = set()
    geography_tags = set()

    for cs in all_case_studies:
        if cs.themes:
            themes.update(cs.themes)
        if cs.geography_tags:
            geography_tags.update(cs.geography_tags)

    return {
        "countries": countries,
        "themes": sorted(list(themes)),
        "geography_tags": sorted(list(geography_tags)),
        "population_bands": pop_bands,
        "revival_types": revival_types
    }


@router.get("/{id}")
def get_case_study(id: int, db: Session = Depends(get_db)):
    """Get a single case study by ID."""
    case_study = db.query(RevivalCaseStudy).filter(RevivalCaseStudy.id == id).first()

    if not case_study:
        raise HTTPException(status_code=404, detail=f"Case study {id} not found")

    return case_study.to_dict()


# ============================================================================
# Similarity Search Endpoint (for RAG)
# ============================================================================

@router.post("/find-similar")
def find_similar_case_studies(
    request: SimilaritySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Find case studies similar to the given parameters.

    This endpoint is used by the AI identity generator to find relevant
    case studies for RAG context.

    Scoring algorithm:
    - +3 points for each matching theme
    - +2 points for each matching geography tag
    - +2 points for matching population band
    - Results sorted by score (highest first)
    """
    all_case_studies = db.query(RevivalCaseStudy).all()

    # Determine population band from population
    search_pop_band = None
    if request.population:
        if request.population < 100:
            search_pop_band = 'under_100'
        elif request.population < 500:
            search_pop_band = '100_500'
        elif request.population < 1000:
            search_pop_band = '500_1000'
        elif request.population < 5000:
            search_pop_band = '1000_5000'
        else:
            search_pop_band = '5000_plus'

    # Score each case study
    scored_results = []

    for cs in all_case_studies:
        score = 0

        # Theme matching (+3 per match)
        if request.themes and cs.themes:
            theme_matches = len(set(request.themes) & set(cs.themes))
            score += theme_matches * 3

        # Geography matching (+2 per match)
        if request.geography and cs.geography_tags:
            geo_matches = len(set(request.geography) & set(cs.geography_tags))
            score += geo_matches * 2

        # Population band matching (+2 if matches)
        if search_pop_band and cs.population_band == search_pop_band:
            score += 2

        if score > 0:
            scored_results.append({
                "case_study": cs.to_dict(),
                "score": score,
                "rag_context": cs.to_rag_context()
            })

    # Sort by score (highest first) and limit
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    limited_results = scored_results[:request.limit]

    return {
        "results": limited_results,
        "total_matches": len(scored_results),
        "search_params": {
            "population": request.population,
            "population_band": search_pop_band,
            "themes": request.themes,
            "geography": request.geography
        }
    }


# ============================================================================
# Admin Endpoints (Platform Admin Only)
# ============================================================================

@router.post("/", status_code=201)
def create_case_study(
    data: CaseStudyCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Create a new case study.

    Requires platform_admin role.
    """
    case_study = RevivalCaseStudy(
        village_name=data.village_name,
        country=data.country,
        region=data.region,
        population_before=data.population_before,
        population_after=data.population_after,
        population_band=data.population_band,
        revival_type=data.revival_type,
        strategy=data.strategy,
        key_projects=data.key_projects,
        outcomes=data.outcomes,
        lessons_learned=data.lessons_learned,
        timeline_years=data.timeline_years,
        themes=data.themes,
        geography_tags=data.geography_tags,
        funding_sources=data.funding_sources,
        sources=data.sources
    )

    db.add(case_study)
    db.commit()
    db.refresh(case_study)

    return case_study.to_dict()


@router.put("/{id}")
def update_case_study(
    id: int,
    data: CaseStudyUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Update a case study.

    Requires platform_admin role.
    """
    case_study = db.query(RevivalCaseStudy).filter(RevivalCaseStudy.id == id).first()

    if not case_study:
        raise HTTPException(status_code=404, detail=f"Case study {id} not found")

    # Update fields if provided
    update_fields = [
        'village_name', 'country', 'region', 'population_before', 'population_after',
        'population_band', 'revival_type', 'strategy', 'key_projects', 'outcomes',
        'lessons_learned', 'timeline_years', 'themes', 'geography_tags',
        'funding_sources', 'sources'
    ]

    for field in update_fields:
        value = getattr(data, field, None)
        if value is not None:
            setattr(case_study, field, value)

    db.commit()
    db.refresh(case_study)

    return case_study.to_dict()


@router.delete("/{id}", status_code=204)
def delete_case_study(
    id: int,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Delete a case study.

    Requires platform_admin role.
    """
    case_study = db.query(RevivalCaseStudy).filter(RevivalCaseStudy.id == id).first()

    if not case_study:
        raise HTTPException(status_code=404, detail=f"Case study {id} not found")

    db.delete(case_study)
    db.commit()

    return None
