"""
Grant matching and application API
Phase E Week 2: Grant Application System

Endpoints:
- POST /api/grants/projects/{id}/match - Get matching funding programs
- GET /api/grants/applications - List applications (with project_id filter)
- POST /api/grants/applications - Create new application
- GET /api/grants/applications/{id} - Get application detail
- PUT /api/grants/applications/{id} - Update application
- DELETE /api/grants/applications/{id} - Delete application
- POST /api/grants/applications/research - AI research assistant
- POST /api/grants/applications/draft - AI application draft
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.project import ProjectInstance, FundingProgram, GrantApplication
from app.models.place import Place
from app.services.claude_api import call_claude_api, build_research_prompt, build_draft_prompt

router = APIRouter(prefix="/api/grants", tags=["grants"])


# ============================================
# PYDANTIC SCHEMAS
# ============================================

class ApplicationCreate(BaseModel):
    project_id: int
    funding_program_id: int
    status: Optional[str] = "draft"
    notes: Optional[str] = None
    amount_requested: Optional[int] = None
    submitted_date: Optional[str] = None
    documents: Optional[List[dict]] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    amount_requested: Optional[int] = None
    amount_approved: Optional[int] = None
    submitted_date: Optional[str] = None
    decision_date: Optional[str] = None
    decision_notes: Optional[str] = None
    documents: Optional[List[dict]] = None


class AIResearchRequest(BaseModel):
    project_id: int
    funding_program_id: int


class AIDraftRequest(BaseModel):
    project_id: int
    funding_program_id: int
    research_notes: Optional[str] = None


# ============================================
# GRANT MATCHING
# ============================================

@router.post("/projects/{project_id}/match")
def match_programs(project_id: int, db: Session = Depends(get_db)):
    """
    Find funding programs that match a project.
    Returns programs sorted by match score.
    """
    project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    village = db.query(Place).filter(Place.id == project.village_id).first()

    # Get all active funding programs
    programs = db.query(FundingProgram).filter(
        FundingProgram.is_active == True
    ).all()

    matches = []
    for prog in programs:
        # Calculate match score (simplified for now)
        score = calculate_match_score(project, village, prog)

        matches.append({
            "program_id": prog.id,
            "name": prog.name,
            "organization": prog.organization,
            "program_type": prog.program_type,
            "level": getattr(prog, 'level', None),
            "score": score,
            "amount_min": prog.amount_min,
            "amount_max": prog.amount_max,
            "funding_percentage_min": prog.funding_percentage_min,
            "funding_percentage_max": prog.funding_percentage_max,
            "deadline_type": prog.deadline_type,
            "deadline_date": prog.next_deadline.isoformat() if prog.next_deadline else None,
            "eligible_themes": prog.eligible_themes,
            "eligible_regions": prog.eligible_regions,
            "eligible_population_bands": prog.eligible_population_bands,
            "description": prog.description,
            "website_url": prog.website_url,
            "application_url": prog.application_url,
            "requirements": prog.requirements,
            "required_documents": prog.required_documents,
            "tips": getattr(prog, 'tips', None),
            "process_summary": getattr(prog, 'process_summary', None),
            "typical_timeline_months": getattr(prog, 'typical_timeline_months', None)
        })

    # Sort by score and return top 15
    sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    return {"matches": sorted_matches[:15]}


def calculate_match_score(project, village, program):
    """
    Calculate how well a funding program matches a project.
    Returns a score from 0-100.
    """
    score = 70  # Base score

    # Budget match
    project_budget = (project.budget_estimated_min or 0) + (project.budget_estimated_max or 0)
    if project_budget > 0:
        avg_budget = project_budget / 2
        if program.amount_min and program.amount_max:
            if program.amount_min <= avg_budget <= program.amount_max:
                score += 10
            elif avg_budget < program.amount_min:
                score += 5  # Project might grow
        elif program.amount_max and avg_budget <= program.amount_max:
            score += 8

    # Theme match (if themes are defined)
    project_themes = project.project_data.get('themes', []) if project.project_data else []
    program_themes = program.eligible_themes or []

    if project_themes and program_themes:
        theme_overlap = len(set(project_themes) & set(program_themes))
        if theme_overlap > 0:
            score += min(15, theme_overlap * 5)

    # Higher funding percentage is better
    if program.funding_percentage_max:
        score += min(5, program.funding_percentage_max // 20)

    return min(100, score)


# ============================================
# GRANT APPLICATIONS CRUD
# ============================================

@router.get("/applications")
def list_applications(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List grant applications.
    Can filter by project_id and/or status.
    """
    query = db.query(GrantApplication).options(
        joinedload(GrantApplication.funding_program)
    )

    if project_id:
        query = query.filter(GrantApplication.project_id == project_id)

    if status:
        query = query.filter(GrantApplication.status == status)

    applications = query.order_by(GrantApplication.created_at.desc()).all()

    return {
        "applications": [
            {
                "id": app.id,
                "project_id": app.project_id,
                "funding_program_id": app.funding_program_id,
                "status": app.status,
                "notes": app.notes,
                "amount_requested": app.amount_requested,
                "amount_approved": app.amount_approved,
                "submitted_date": app.submitted_date.isoformat() if app.submitted_date else None,
                "decision_date": app.decision_date.isoformat() if app.decision_date else None,
                "decision_notes": app.decision_notes,
                "documents": app.documents,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
                "funding_program": {
                    "id": app.funding_program.id,
                    "name": app.funding_program.name,
                    "organization": app.funding_program.organization,
                    "amount_min": app.funding_program.amount_min,
                    "amount_max": app.funding_program.amount_max,
                    "funding_percentage_max": app.funding_program.funding_percentage_max,
                    "deadline_type": app.funding_program.deadline_type,
                    "deadline_date": app.funding_program.next_deadline.isoformat() if app.funding_program.next_deadline else None,
                    "required_documents": app.funding_program.required_documents,
                    "typical_timeline_months": getattr(app.funding_program, 'typical_timeline_months', None)
                } if app.funding_program else None
            }
            for app in applications
        ]
    }


@router.post("/applications")
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create a new grant application."""
    # Verify project exists
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == application.project_id
    ).first()
    if not project:
        raise HTTPException(404, "Project not found")

    # Verify funding program exists
    program = db.query(FundingProgram).filter(
        FundingProgram.id == application.funding_program_id
    ).first()
    if not program:
        raise HTTPException(404, "Funding program not found")

    # Check if application already exists for this project/program combo
    existing = db.query(GrantApplication).filter(
        GrantApplication.project_id == application.project_id,
        GrantApplication.funding_program_id == application.funding_program_id
    ).first()
    if existing:
        raise HTTPException(400, "Application already exists for this project and program")

    # Parse submitted_date if provided
    submitted_date = None
    if application.submitted_date:
        try:
            submitted_date = datetime.fromisoformat(application.submitted_date.replace('Z', '+00:00'))
        except ValueError:
            pass

    # Create application
    new_app = GrantApplication(
        project_id=application.project_id,
        funding_program_id=application.funding_program_id,
        status=application.status or "draft",
        notes=application.notes,
        amount_requested=application.amount_requested,
        submitted_date=submitted_date,
        documents=application.documents
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return {
        "success": True,
        "message": "Application created successfully",
        "application": {
            "id": new_app.id,
            "project_id": new_app.project_id,
            "funding_program_id": new_app.funding_program_id,
            "status": new_app.status,
            "created_at": new_app.created_at.isoformat() if new_app.created_at else None
        }
    }


@router.get("/applications/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific grant application."""
    app = db.query(GrantApplication).options(
        joinedload(GrantApplication.funding_program),
        joinedload(GrantApplication.project)
    ).filter(GrantApplication.id == application_id).first()

    if not app:
        raise HTTPException(404, "Application not found")

    return app.to_dict()


@router.put("/applications/{application_id}")
def update_application(
    application_id: int,
    update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a grant application."""
    app = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not app:
        raise HTTPException(404, "Application not found")

    # Update fields if provided
    if update.status is not None:
        app.status = update.status

    if update.notes is not None:
        app.notes = update.notes

    if update.amount_requested is not None:
        app.amount_requested = update.amount_requested

    if update.amount_approved is not None:
        app.amount_approved = update.amount_approved

    if update.submitted_date is not None:
        try:
            app.submitted_date = datetime.fromisoformat(update.submitted_date.replace('Z', '+00:00'))
        except ValueError:
            pass

    if update.decision_date is not None:
        try:
            app.decision_date = datetime.fromisoformat(update.decision_date.replace('Z', '+00:00'))
        except ValueError:
            pass

    if update.decision_notes is not None:
        app.decision_notes = update.decision_notes

    if update.documents is not None:
        app.documents = update.documents

    app.updated_at = datetime.now()

    db.commit()
    db.refresh(app)

    return {
        "success": True,
        "message": "Application updated successfully",
        "application": app.to_dict()
    }


@router.delete("/applications/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete a grant application."""
    app = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not app:
        raise HTTPException(404, "Application not found")

    db.delete(app)
    db.commit()

    return {
        "success": True,
        "message": "Application deleted successfully"
    }


# ============================================
# FUNDING PROGRAMS (Read-only)
# ============================================

@router.get("/funding-programs")
def list_funding_programs(
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List all funding programs."""
    query = db.query(FundingProgram)

    if active_only:
        query = query.filter(FundingProgram.is_active == True)

    programs = query.order_by(FundingProgram.name).all()

    return {
        "programs": [prog.to_dict() for prog in programs],
        "total": len(programs)
    }


@router.get("/funding-programs/{program_id}")
def get_funding_program(program_id: int, db: Session = Depends(get_db)):
    """Get a specific funding program."""
    program = db.query(FundingProgram).filter(
        FundingProgram.id == program_id
    ).first()

    if not program:
        raise HTTPException(404, "Funding program not found")

    return program.to_dict()


# ============================================
# AI-POWERED GRANT ASSISTANCE
# ============================================

@router.post("/applications/research")
async def generate_research(
    request: AIResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered research content for a grant application.
    Used in the "Researching" stage to analyze eligibility and requirements.
    """
    # Get project details
    project = db.query(ProjectInstance).options(
        joinedload(ProjectInstance.place)
    ).filter(ProjectInstance.id == request.project_id).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Get funding program details
    program = db.query(FundingProgram).filter(
        FundingProgram.id == request.funding_program_id
    ).first()

    if not program:
        raise HTTPException(404, "Funding program not found")

    # Extract project data
    project_data = project.project_data or {}
    project_name = project_data.get('title') or project_data.get('name') or "Projet sans nom"
    project_description = project_data.get('description') or project_data.get('narrative') or ""

    # Get village info
    village = project.place
    village_name = village.name if village else "Village"
    village_population = village.population if village else None
    village_region = "Nouvelle-Aquitaine, Charente"

    try:
        # Build prompt
        prompt = build_research_prompt(
            village_name=village_name,
            village_population=village_population,
            village_region=village_region,
            project_name=project_name,
            project_description=project_description,
            budget_min=project.budget_estimated_min,
            budget_max=project.budget_estimated_max,
            timeline_months=project.timeline_months,
            program_name=program.name,
            program_organization=program.organization,
            amount_min=program.amount_min,
            amount_max=program.amount_max,
            funding_percentage_min=program.funding_percentage_min,
            funding_percentage_max=program.funding_percentage_max,
            requirements=program.requirements,
            eligible_themes=program.eligible_themes,
            eligible_population_bands=program.eligible_population_bands,
            required_documents=program.required_documents
        )

        # Call Claude API
        research_content = await call_claude_api(prompt)

        return {
            "success": True,
            "research_content": research_content,
            "project_name": project_name,
            "program_name": program.name
        }

    except Exception as e:
        raise HTTPException(500, f"AI generation failed: {str(e)}")


@router.post("/applications/draft")
async def generate_draft(
    request: AIDraftRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered application draft for a grant.
    Used in the "Preparing" stage to draft the full application.
    """
    # Get project details
    project = db.query(ProjectInstance).options(
        joinedload(ProjectInstance.place)
    ).filter(ProjectInstance.id == request.project_id).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Get funding program details
    program = db.query(FundingProgram).filter(
        FundingProgram.id == request.funding_program_id
    ).first()

    if not program:
        raise HTTPException(404, "Funding program not found")

    # Extract project data
    project_data = project.project_data or {}
    project_name = project_data.get('title') or project_data.get('name') or "Projet sans nom"
    project_description = project_data.get('description') or project_data.get('narrative') or ""

    # Get village info
    village = project.place
    village_name = village.name if village else "Village"
    village_population = village.population if village else None
    village_region = "Nouvelle-Aquitaine, Charente"

    try:
        # Build prompt
        prompt = build_draft_prompt(
            village_name=village_name,
            village_population=village_population,
            village_region=village_region,
            project_name=project_name,
            project_description=project_description,
            budget_min=project.budget_estimated_min,
            budget_max=project.budget_estimated_max,
            timeline_months=project.timeline_months,
            program_name=program.name,
            program_organization=program.organization,
            amount_min=program.amount_min,
            amount_max=program.amount_max,
            funding_percentage_min=program.funding_percentage_min,
            funding_percentage_max=program.funding_percentage_max,
            requirements=program.requirements,
            eligible_themes=program.eligible_themes,
            required_documents=program.required_documents,
            research_notes=request.research_notes
        )

        # Call Claude API
        draft_content = await call_claude_api(prompt, max_tokens=6000)

        return {
            "success": True,
            "draft_content": draft_content,
            "project_name": project_name,
            "program_name": program.name
        }

    except Exception as e:
        raise HTTPException(500, f"AI generation failed: {str(e)}")
