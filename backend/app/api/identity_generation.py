"""
Identity Generation API - Real Claude API integration with RAG context

Replaces the mock generator with actual AI-powered identity generation.
"""
import logging
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Village, User
from app.services.ai_identity_engine import AIIdentityEngine, get_ai_engine
from app.middleware.auth import get_current_user

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/identity", tags=["identity-generation"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class AuditData(BaseModel):
    """Audit data from the 5-step wizard"""
    # Step 1: History & Heritage
    warPeriods: Optional[List[str]] = []
    eventTypes: Optional[List[str]] = []
    monuments: Optional[str] = None
    legends: Optional[str] = None
    historyNotes: Optional[str] = None

    # Step 2: Environment & Resources
    waterFeatures: Optional[List[str]] = []
    landscape: Optional[List[str]] = []
    agriculture: Optional[str] = None
    naturalResources: Optional[str] = None
    environmentNotes: Optional[str] = None

    # Step 3: Economy, Traditions & Life
    localProducts: Optional[List[str]] = []
    potentialProducts: Optional[str] = None
    festivals: Optional[str] = None
    services: Optional[List[str]] = []
    vibe: Optional[str] = None
    nearestTown: Optional[str] = None
    livingDescription: Optional[str] = None

    # Step 4: Free Description
    freeDescription: Optional[str] = None


class GenerateIdentityRequest(BaseModel):
    """Request body for generating identity options"""
    village_slug: str
    audit_data: AuditData
    num_options: int = 3  # Default to 3 options for 3-tier system


class ProjectFunding(BaseModel):
    program_name: str
    match_score: float
    why_relevant: str
    estimated_amount: str


class ProjectInspiration(BaseModel):
    village_name: str
    relevance: str


class Project(BaseModel):
    title: str
    description: str
    timeline_months: int
    budget_min: int
    budget_max: int
    difficulty: str
    inspired_by: Optional[ProjectInspiration] = None
    potential_funding: List[ProjectFunding] = []
    first_steps: List[str] = []


class IdentityOption(BaseModel):
    tier: Optional[int] = None
    tier_label: Optional[str] = None
    identity_title: str
    identity_narrative: str
    confidence: float
    themes: List[str]
    summary_identity: str
    live_here_summary: str
    projects: List[Project]


class GenerateIdentityResponse(BaseModel):
    options: List[IdentityOption]
    metadata: Dict[str, Any]


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate", response_model=GenerateIdentityResponse)
def generate_identity_options(
    request: GenerateIdentityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered identity options for a village.

    Uses Claude API with RAG context from:
    - Similar case studies
    - Matching funding programs

    Requires authentication. Village admins can only generate for their village.
    Platform admins can generate for any village.
    """
    logger.info(f"Identity generation requested for village: {request.village_slug}")
    logger.info(f"User: {current_user.email}, Role: {current_user.role}")

    try:
        # Verify village exists
        village = db.query(Village).filter(Village.slug == request.village_slug).first()
        if not village:
            logger.error(f"Village not found: {request.village_slug}")
            raise HTTPException(status_code=404, detail=f"Village not found: {request.village_slug}")

        logger.info(f"Village found: {village.name} (id={village.id})")

        # Check authorization (village admin can only access their village)
        if current_user.role == "village_admin":
            if current_user.village_id != village.id:
                logger.warning(f"User {current_user.email} tried to access village {village.slug} but is assigned to village_id {current_user.village_id}")
                raise HTTPException(
                    status_code=403,
                    detail="You can only generate identity for your own village"
                )

        # Convert audit data to dict
        audit_dict = request.audit_data.dict()
        logger.info(f"Audit data keys: {list(audit_dict.keys())}")

        # Initialize AI engine
        try:
            engine = get_ai_engine()
            logger.info("AI engine initialized successfully")
        except ValueError as e:
            logger.error(f"AI engine initialization failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI engine initialization failed: {str(e)}. Make sure ANTHROPIC_API_KEY is set."
            )

        # Generate identity options
        logger.info("Starting identity generation...")
        result = engine.generate_identity_options(
            db=db,
            village_slug=request.village_slug,
            audit_data=audit_dict,
            num_options=request.num_options
        )

        logger.info(f"Identity generation completed. Options generated: {len(result.get('options', []))}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Identity generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Identity generation failed: {str(e)}"
        )


@router.post("/generate-preview")
def generate_identity_preview(
    request: GenerateIdentityRequest,
    db: Session = Depends(get_db)
):
    """
    Preview identity generation without saving.

    This endpoint is public (no auth required) for demo purposes.
    In production, you may want to add rate limiting.
    """
    logger.info(f"Identity preview requested for village: {request.village_slug}")

    try:
        # Verify village exists
        village = db.query(Village).filter(Village.slug == request.village_slug).first()
        if not village:
            logger.error(f"Village not found: {request.village_slug}")
            raise HTTPException(status_code=404, detail=f"Village not found: {request.village_slug}")

        logger.info(f"Village found: {village.name} (id={village.id})")

        # Convert audit data to dict
        audit_dict = request.audit_data.dict()
        logger.info(f"Audit data keys: {list(audit_dict.keys())}")

        # Initialize AI engine
        try:
            engine = get_ai_engine()
            logger.info("AI engine initialized successfully")
        except ValueError as e:
            logger.error(f"AI engine initialization failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI engine not configured. Set ANTHROPIC_API_KEY environment variable."
            )

        # Generate identity options
        logger.info("Starting identity preview generation...")
        result = engine.generate_identity_options(
            db=db,
            village_slug=request.village_slug,
            audit_data=audit_dict,
            num_options=request.num_options
        )

        logger.info(f"Identity preview completed. Options generated: {len(result.get('options', []))}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Identity preview failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Identity generation failed: {str(e)}"
        )


@router.get("/rag-context/{village_slug}")
def get_rag_context_preview(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """
    Preview the RAG context that would be used for a village.

    Returns similar case studies and matching funding programs
    based on the village's existing data.

    Useful for debugging and understanding AI inputs.
    """
    # Verify village exists
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village not found: {village_slug}")

    try:
        engine = get_ai_engine()
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI engine not configured: {str(e)}"
        )

    # Get village's themes if available
    themes = village.themes if hasattr(village, 'themes') and village.themes else []

    # Get similar case studies
    similar_case_studies = engine.find_similar_case_studies(
        db,
        population=village.population,
        themes=themes,
        geography=[],  # Would come from audit
        limit=5
    )

    # Get matching funding programs
    matching_funding = engine.find_matching_funding(
        db,
        themes=themes,
        budget=100000,
        population=village.population,
        limit=8
    )

    return {
        "village": {
            "slug": village.slug,
            "name": village.name,
            "population": village.population,
            "themes": themes
        },
        "similar_case_studies": [
            {
                "village_name": item["case_study"].village_name,
                "country": item["case_study"].country,
                "region": item["case_study"].region,
                "revival_type": item["case_study"].revival_type,
                "strategy": item["case_study"].strategy[:200] + "..." if len(item["case_study"].strategy) > 200 else item["case_study"].strategy,
                "score": item["score"]
            }
            for item in similar_case_studies
        ],
        "matching_funding": [
            {
                "name": item["program"].name,
                "organization": item["program"].organization,
                "funding_type": item["program"].funding_type,
                "amount_range": f"€{item['program'].amount_min or 0:,}-€{item['program'].amount_max or 0:,}",
                "score": item["score"],
                "match_reasons": item["match_reasons"]
            }
            for item in matching_funding
        ]
    }


@router.get("/cost-estimate")
def get_generation_cost_estimate():
    """
    Get estimated cost per identity generation.

    Returns cost breakdown for API calls.
    """
    return {
        "model": "claude-sonnet-4-20250514",
        "estimated_tokens": {
            "input": 3000,
            "output": 2500
        },
        "pricing": {
            "input_per_million": 3.00,
            "output_per_million": 15.00
        },
        "estimated_cost_per_generation": {
            "usd": 0.0465,
            "eur": 0.043
        },
        "cost_for_3_options": {
            "usd": 0.0465,
            "eur": 0.043,
            "note": "Single API call generates all 3 options"
        },
        "annual_cost_per_village": {
            "estimate": "~$1.50 for initial generation + refinements",
            "note": "Based on 3-4 generation rounds per year"
        }
    }
