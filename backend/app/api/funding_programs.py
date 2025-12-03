"""
Funding Programs API - CRUD endpoints + matching for project funding
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.database import get_db
from app.models.funding_program import FundingProgram


router = APIRouter(prefix="/api/funding-programs", tags=["funding-programs"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class FundingProgramCreate(BaseModel):
    name: str
    provider: str
    country: str
    eligible_themes: Optional[List[str]] = None
    eligible_population_max: Optional[int] = None
    funding_type: Optional[str] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    funding_percentage_max: Optional[int] = None
    application_url: Optional[str] = None
    deadline_type: Optional[str] = None
    deadline_date: Optional[date] = None
    process_summary: Optional[str] = None
    typical_timeline_months: Optional[int] = None
    tips: Optional[str] = None
    sources: Optional[List[str]] = None
    is_active: bool = True


class FundingProgramUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    country: Optional[str] = None
    eligible_themes: Optional[List[str]] = None
    eligible_population_max: Optional[int] = None
    funding_type: Optional[str] = None
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    funding_percentage_max: Optional[int] = None
    application_url: Optional[str] = None
    deadline_type: Optional[str] = None
    deadline_date: Optional[date] = None
    process_summary: Optional[str] = None
    typical_timeline_months: Optional[int] = None
    tips: Optional[str] = None
    sources: Optional[List[str]] = None
    is_active: Optional[bool] = None


class FundingMatchRequest(BaseModel):
    themes: Optional[List[str]] = None
    budget: Optional[int] = None
    population: Optional[int] = None
    limit: int = 5


# ============================================================================
# Public Endpoints
# ============================================================================

@router.get("/")
def list_funding_programs(
    country: Optional[str] = Query(None, description="Filter by country"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    theme: Optional[str] = Query(None, description="Filter by eligible theme"),
    funding_type: Optional[str] = Query(None, description="Filter by funding type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    max_budget: Optional[int] = Query(None, description="Filter programs that can fund up to this amount"),
    search: Optional[str] = Query(None, description="Search in name and process summary"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all funding programs with optional filters.

    - **country**: Filter by country (e.g., 'France')
    - **provider**: Filter by provider (e.g., 'EU', 'État')
    - **theme**: Filter by eligible theme (e.g., 'heritage', 'ecology')
    - **funding_type**: Filter by type (e.g., 'grant', 'loan')
    - **is_active**: Filter by active status
    - **max_budget**: Show programs that can fund projects up to this amount
    - **search**: Search in name and process summary
    """
    query = db.query(FundingProgram)

    if country:
        query = query.filter(FundingProgram.country == country)

    if provider:
        query = query.filter(FundingProgram.provider.ilike(f"%{provider}%"))

    if theme:
        query = query.filter(FundingProgram.eligible_themes.contains([theme]))

    if funding_type:
        query = query.filter(FundingProgram.funding_type == funding_type)

    if is_active is not None:
        query = query.filter(FundingProgram.is_active == is_active)

    if max_budget:
        # Show programs where amount_max >= max_budget (can fund the project)
        query = query.filter(
            or_(
                FundingProgram.amount_max >= max_budget,
                FundingProgram.amount_max.is_(None)
            )
        )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                FundingProgram.name.ilike(search_term),
                FundingProgram.process_summary.ilike(search_term)
            )
        )

    total = query.count()
    programs = query.order_by(FundingProgram.name).offset(offset).limit(limit).all()

    return {
        "results": [p.to_dict() for p in programs],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/filters")
def get_funding_program_filters(db: Session = Depends(get_db)):
    """
    Get available filter options for funding programs.

    Returns distinct values for countries, providers, themes, and funding types.
    """
    # Get distinct countries
    countries = db.query(FundingProgram.country).distinct().all()
    countries = sorted([c[0] for c in countries if c[0]])

    # Get distinct providers
    providers = db.query(FundingProgram.provider).distinct().all()
    providers = sorted([p[0] for p in providers if p[0]])

    # Get distinct funding types
    funding_types = db.query(FundingProgram.funding_type).distinct().all()
    funding_types = sorted([f[0] for f in funding_types if f[0]])

    # Get distinct deadline types
    deadline_types = db.query(FundingProgram.deadline_type).distinct().all()
    deadline_types = sorted([d[0] for d in deadline_types if d[0]])

    # Get all themes (from arrays)
    all_programs = db.query(FundingProgram).all()
    themes = set()

    for prog in all_programs:
        if prog.eligible_themes:
            themes.update(prog.eligible_themes)

    return {
        "countries": countries,
        "providers": providers,
        "themes": sorted(list(themes)),
        "funding_types": funding_types,
        "deadline_types": deadline_types
    }


@router.get("/{id}")
def get_funding_program(id: int, db: Session = Depends(get_db)):
    """Get a single funding program by ID."""
    program = db.query(FundingProgram).filter(FundingProgram.id == id).first()

    if not program:
        raise HTTPException(status_code=404, detail=f"Funding program {id} not found")

    return program.to_dict()


# ============================================================================
# Funding Match Endpoint (for RAG)
# ============================================================================

@router.post("/match")
def match_funding_programs(
    request: FundingMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Find funding programs that match project parameters.

    This endpoint is used by the AI identity generator to find relevant
    funding programs for suggested projects.

    Scoring algorithm:
    - +3 points for each matching theme
    - +2 points if budget falls within amount range
    - +1 point if population is under eligible_population_max
    - Active programs get +1 bonus
    - Results sorted by score (highest first)
    """
    # Only consider active programs by default
    programs = db.query(FundingProgram).filter(FundingProgram.is_active == True).all()

    # Score each program
    scored_results = []

    for prog in programs:
        score = 0
        match_reasons = []

        # Theme matching (+3 per match)
        if request.themes and prog.eligible_themes:
            theme_matches = set(request.themes) & set(prog.eligible_themes)
            if theme_matches:
                score += len(theme_matches) * 3
                match_reasons.append(f"Matching themes: {', '.join(theme_matches)}")

        # Budget range matching (+2 if within range)
        if request.budget and prog.amount_max:
            if prog.amount_min and prog.amount_min <= request.budget <= prog.amount_max:
                score += 2
                match_reasons.append(f"Budget within range (€{prog.amount_min:,}-€{prog.amount_max:,})")
            elif request.budget <= prog.amount_max:
                score += 2
                match_reasons.append(f"Budget under max (up to €{prog.amount_max:,})")

        # Population eligibility (+1 if eligible)
        if request.population and prog.eligible_population_max:
            if request.population <= prog.eligible_population_max:
                score += 1
                match_reasons.append(f"Population eligible (max {prog.eligible_population_max:,})")

        # Active bonus (+1)
        if prog.is_active:
            score += 1

        if score > 1:  # At least some match beyond just being active
            # Calculate estimated funding
            estimated_amount = None
            if prog.funding_percentage_max and request.budget:
                estimated_amount = int(request.budget * prog.funding_percentage_max / 100)

            scored_results.append({
                "program": prog.to_dict(),
                "score": score,
                "match_reasons": match_reasons,
                "estimated_amount": estimated_amount,
                "rag_context": prog.to_rag_context()
            })

    # Sort by score (highest first) and limit
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    limited_results = scored_results[:request.limit]

    return {
        "results": limited_results,
        "total_matches": len(scored_results),
        "search_params": {
            "themes": request.themes,
            "budget": request.budget,
            "population": request.population
        }
    }


# ============================================================================
# Admin Endpoints (Platform Admin Only)
# ============================================================================

@router.post("/", status_code=201)
def create_funding_program(
    data: FundingProgramCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Create a new funding program.

    Requires platform_admin role.
    """
    program = FundingProgram(
        name=data.name,
        provider=data.provider,
        country=data.country,
        eligible_themes=data.eligible_themes,
        eligible_population_max=data.eligible_population_max,
        funding_type=data.funding_type,
        amount_min=data.amount_min,
        amount_max=data.amount_max,
        funding_percentage_max=data.funding_percentage_max,
        application_url=data.application_url,
        deadline_type=data.deadline_type,
        deadline_date=data.deadline_date,
        process_summary=data.process_summary,
        typical_timeline_months=data.typical_timeline_months,
        tips=data.tips,
        sources=data.sources,
        is_active=data.is_active
    )

    db.add(program)
    db.commit()
    db.refresh(program)

    return program.to_dict()


@router.put("/{id}")
def update_funding_program(
    id: int,
    data: FundingProgramUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Update a funding program.

    Requires platform_admin role.
    """
    program = db.query(FundingProgram).filter(FundingProgram.id == id).first()

    if not program:
        raise HTTPException(status_code=404, detail=f"Funding program {id} not found")

    # Update fields if provided
    update_fields = [
        'name', 'provider', 'country', 'eligible_themes', 'eligible_population_max',
        'funding_type', 'amount_min', 'amount_max', 'funding_percentage_max',
        'application_url', 'deadline_type', 'deadline_date', 'process_summary',
        'typical_timeline_months', 'tips', 'sources', 'is_active'
    ]

    for field in update_fields:
        value = getattr(data, field, None)
        if value is not None:
            setattr(program, field, value)

    db.commit()
    db.refresh(program)

    return program.to_dict()


@router.delete("/{id}", status_code=204)
def delete_funding_program(
    id: int,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_platform_admin)
):
    """
    Delete a funding program.

    Requires platform_admin role.
    """
    program = db.query(FundingProgram).filter(FundingProgram.id == id).first()

    if not program:
        raise HTTPException(status_code=404, detail=f"Funding program {id} not found")

    db.delete(program)
    db.commit()

    return None
