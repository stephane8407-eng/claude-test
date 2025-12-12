"""
Phase E Week 2: Grant Application API Routes

Provides endpoints for:
- Matching projects to funding programs
- Generating grant applications using Claude API
- Managing grant application lifecycle
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.grant_application import GrantApplication
from app.models.project_instance import ProjectInstance
from app.models.funding_program import FundingProgram
from app.models.village import Village
from app.services.grant_matcher import GrantMatcher


router = APIRouter(prefix="/api/grants", tags=["grants"])


# ============================================
# PYDANTIC SCHEMAS
# ============================================

class MatchGrantsRequest(BaseModel):
    """Request to match funding programs for a project"""
    village_population: int
    village_region: Optional[str] = None
    limit: int = 10
    min_score: int = 0


class GenerateApplicationRequest(BaseModel):
    """Request to generate a grant application"""
    program_id: int
    village_name: str
    village_population: int
    village_region: Optional[str] = None
    village_department: Optional[str] = None
    maire_name: Optional[str] = None
    additional_context: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    """Request to update a grant application"""
    text: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    amount_requested: Optional[int] = None
    ai_research: Optional[str] = None
    ai_draft: Optional[str] = None


class RegenerateSectionRequest(BaseModel):
    """Request to regenerate a section of an application"""
    section_name: str
    instructions: Optional[str] = None


class AIResearchRequest(BaseModel):
    """Request for AI-powered grant research"""
    project_id: int
    funding_program_id: int


class AIDraftRequest(BaseModel):
    """Request for AI-powered draft generation"""
    project_id: int
    funding_program_id: int
    research_notes: Optional[str] = None


class GrantApplicationCreate(BaseModel):
    """Request to create a grant application"""
    project_id: int
    funding_program_id: int
    status: str = "draft"
    generated_content: Optional[str] = None
    amount_requested: Optional[int] = None
    notes: Optional[str] = None


# ============================================
# MATCH FUNDING PROGRAMS
# ============================================

@router.post("/projects/{project_id}/match")
def match_funding_programs(
    project_id: int,
    request: MatchGrantsRequest,
    db: Session = Depends(get_db)
):
    """
    Find and rank matching funding programs for a project.
    
    Scoring based on:
    - Population band match (30 pts)
    - Theme overlap (30 pts)
    - Budget compatibility (25 pts)
    - Deadline type (15 pts)
    """
    # Verify project exists
    project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    matches = GrantMatcher.match_programs(
        db=db,
        project_id=project_id,
        village_population=request.village_population,
        village_region=request.village_region,
        limit=request.limit,
        min_score=request.min_score
    )

    return {
        "project_id": project_id,
        "village_population": request.village_population,
        "total_programs": db.query(FundingProgram).filter(FundingProgram.is_active == True).count(),
        "matches_found": len(matches),
        "matches": matches
    }


@router.get("/projects/{project_id}/match/quick")
def quick_match_funding_programs(
    project_id: int,
    population: int,
    region: Optional[str] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Quick match endpoint with query parameters (for simpler frontend calls)"""
    project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    matches = GrantMatcher.match_programs(
        db=db,
        project_id=project_id,
        village_population=population,
        village_region=region,
        limit=limit
    )

    return {"matches": matches}


# ============================================
# GENERATE APPLICATION
# ============================================

@router.post("/projects/{project_id}/generate")
def generate_grant_application(
    project_id: int,
    request: GenerateApplicationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a complete French grant application using Claude API.
    
    Creates a professional administrative document including:
    - Cover letter
    - Commune presentation
    - Detailed project description
    - Budget breakdown
    - Implementation timeline
    """
    # Verify project exists
    project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # Verify program exists
    program = db.query(FundingProgram).filter(FundingProgram.id == request.program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme de financement non trouvé")

    try:
        from app.services.application_generator import ApplicationGenerator
        generator = ApplicationGenerator()
        
        result = generator.generate_application(
            db=db,
            project_id=project_id,
            program_id=request.program_id,
            village_name=request.village_name,
            village_population=request.village_population,
            village_region=request.village_region,
            village_department=request.village_department,
            maire_name=request.maire_name,
            additional_context=request.additional_context
        )
        
        return {
            "success": True,
            "message": "Dossier de demande généré avec succès",
            **result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la génération du dossier: {str(e)}"
        )


# ============================================
# GET APPLICATION
# ============================================

@router.get("/applications/{application_id}")
def get_grant_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get a grant application by ID"""
    application = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    # Get related program info
    program = db.query(FundingProgram).filter(
        FundingProgram.id == application.funding_program_id
    ).first()

    # Get related project info
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == application.project_id
    ).first()

    return {
        "id": application.id,
        "project_id": application.project_id,
        "project_title": project.project_data.get('title') if project and project.project_data else None,
        "funding_program_id": application.funding_program_id,
        "program_name": program.name if program else None,
        "program_provider": program.organization if program else None,
        "text": application.generated_content,
        "ai_research": application.ai_research,
        "ai_draft": application.ai_draft,
        "status": application.status,
        "amount_requested": application.amount_requested,
        "amount_approved": application.amount_approved,
        "submitted_date": application.submitted_date.isoformat() if application.submitted_date else None,
        "decision_date": application.decision_date.isoformat() if application.decision_date else None,
        "decision_notes": application.decision_notes,
        "notes": application.notes,
        "documents": application.documents or [],
        "created_at": application.created_at.isoformat() if application.created_at else None,
        "updated_at": application.updated_at.isoformat() if application.updated_at else None
    }


# ============================================
# UPDATE APPLICATION
# ============================================

@router.put("/applications/{application_id}")
def update_grant_application(
    application_id: int,
    request: UpdateApplicationRequest,
    db: Session = Depends(get_db)
):
    """Update a grant application (edit text, change status, add notes)"""
    application = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    # Validate status if provided
    if request.status:
        if request.status not in GrantApplication.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Statut invalide. Valeurs acceptées: {', '.join(GrantApplication.VALID_STATUSES)}"
            )
        application.status = request.status

    if request.text is not None:
        application.generated_content = request.text

    if request.notes is not None:
        application.notes = request.notes

    if request.amount_requested is not None:
        application.amount_requested = request.amount_requested

    if request.ai_research is not None:
        application.ai_research = request.ai_research

    if request.ai_draft is not None:
        application.ai_draft = request.ai_draft

    db.commit()
    db.refresh(application)

    return {
        "success": True,
        "message": "Dossier mis à jour",
        "application_id": application.id,
        "status": application.status
    }


# ============================================
# LIST APPLICATIONS FOR PROJECT
# ============================================

@router.get("/projects/{project_id}/applications")
def list_project_applications(
    project_id: int,
    db: Session = Depends(get_db)
):
    """List all grant applications for a project"""
    # Verify project exists
    project = db.query(ProjectInstance).filter(ProjectInstance.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    applications = db.query(GrantApplication).filter(
        GrantApplication.project_id == project_id
    ).order_by(GrantApplication.created_at.desc()).all()

    result = []
    for app in applications:
        program = db.query(FundingProgram).filter(
            FundingProgram.id == app.funding_program_id
        ).first()
        
        result.append({
            'id': app.id,
            'funding_program_id': app.funding_program_id,
            'program_name': program.name if program else 'Programme inconnu',
            'program_provider': program.organization if program else None,
            'status': app.status,
            'amount_requested': app.amount_requested,
            'created_at': app.created_at.isoformat() if app.created_at else None
        })

    return {
        'project_id': project_id,
        'count': len(result),
        'applications': result
    }


# ============================================
# DELETE APPLICATION
# ============================================

@router.delete("/applications/{application_id}")
def delete_grant_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Delete a grant application (only if in draft status)"""
    application = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    if application.status != 'draft':
        raise HTTPException(
            status_code=400,
            detail="Seuls les dossiers en brouillon peuvent être supprimés"
        )

    db.delete(application)
    db.commit()

    return {
        "success": True,
        "message": "Dossier supprimé"
    }


# ============================================
# REGENERATE SECTION
# ============================================

@router.post("/applications/{application_id}/regenerate-section")
def regenerate_application_section(
    application_id: int,
    request: RegenerateSectionRequest,
    db: Session = Depends(get_db)
):
    """Regenerate a specific section of an application"""
    application = db.query(GrantApplication).filter(
        GrantApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")

    try:
        from app.services.application_generator import ApplicationGenerator
        generator = ApplicationGenerator()
        
        result = generator.regenerate_section(
            db=db,
            application_id=application_id,
            section_name=request.section_name,
            instructions=request.instructions
        )
        
        return {
            "success": True,
            "section": result['section'],
            "new_content": result['new_content']
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la régénération: {str(e)}"
        )


# ============================================
# FUNDING PROGRAMS STATS
# ============================================

@router.get("/programs/stats")
def get_funding_programs_stats(db: Session = Depends(get_db)):
    """Get statistics about available funding programs"""
    programs = db.query(FundingProgram).filter(FundingProgram.is_active == True).all()

    by_level = {}
    by_deadline = {}
    total_amount_min = 0
    total_amount_max = 0

    for p in programs:
        level = p.level or 'Other'
        by_level[level] = by_level.get(level, 0) + 1
        
        deadline = p.deadline_type or 'unknown'
        by_deadline[deadline] = by_deadline.get(deadline, 0) + 1
        
        if p.amount_min:
            total_amount_min += p.amount_min
        if p.amount_max:
            total_amount_max += p.amount_max

    return {
        "total_programs": len(programs),
        "by_level": by_level,
        "by_deadline_type": by_deadline,
        "funding_range": {
            "min_total": total_amount_min,
            "max_total": total_amount_max,
            "average_min": total_amount_min // len(programs) if programs else 0,
            "average_max": total_amount_max // len(programs) if programs else 0
        }
    }


# ============================================
# AI RESEARCH & DRAFT GENERATION
# ============================================

@router.post("/applications/research")
def generate_ai_research(
    request: AIResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered research for a grant application.

    Analyzes the project and funding program to produce:
    - Eligibility assessment
    - Key requirements summary
    - Recommended approach
    - Potential challenges

    Also saves the generated content to the database (creates or updates application).

    Note: This endpoint calls the Claude API and may take 3-10 seconds.
    """
    # Verify project exists
    project = db.query(ProjectInstance).filter(ProjectInstance.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # Verify program exists
    program = db.query(FundingProgram).filter(FundingProgram.id == request.funding_program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme de financement non trouvé")

    try:
        from app.services.application_generator import ApplicationGenerator
        generator = ApplicationGenerator()

        result = generator.research_eligibility(
            db=db,
            project_id=request.project_id,
            program_id=request.funding_program_id
        )

        # Find or create application record to save the research
        application = db.query(GrantApplication).filter(
            GrantApplication.project_id == request.project_id,
            GrantApplication.funding_program_id == request.funding_program_id
        ).first()

        if application:
            # Update existing application
            application.ai_research = result['research_content']
        else:
            # Create new application with the research
            application = GrantApplication(
                project_id=request.project_id,
                funding_program_id=request.funding_program_id,
                status='draft',
                ai_research=result['research_content']
            )
            db.add(application)

        db.commit()
        db.refresh(application)

        return {
            "success": True,
            "research_content": result['research_content'],
            "project_id": result['project_id'],
            "funding_program_id": result['program_id'],
            "project_title": result['project_title'],
            "program_name": result['program_name'],
            "application_id": application.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse d'éligibilité: {str(e)}"
        )


@router.post("/applications/draft")
def generate_ai_draft(
    request: AIDraftRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered draft for a grant application.

    Creates a structured application draft based on:
    - Project information
    - Funding program requirements
    - Optional research notes

    Also saves the generated content to the database (creates or updates application).

    Note: This endpoint calls the Claude API and may take 5-15 seconds.
    """
    # Verify project exists
    project = db.query(ProjectInstance).filter(ProjectInstance.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # Verify program exists
    program = db.query(FundingProgram).filter(FundingProgram.id == request.funding_program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme de financement non trouvé")

    try:
        from app.services.application_generator import ApplicationGenerator
        generator = ApplicationGenerator()

        result = generator.generate_draft(
            db=db,
            project_id=request.project_id,
            program_id=request.funding_program_id,
            research_notes=request.research_notes
        )

        # Find or create application record to save the draft
        application = db.query(GrantApplication).filter(
            GrantApplication.project_id == request.project_id,
            GrantApplication.funding_program_id == request.funding_program_id
        ).first()

        if application:
            # Update existing application
            application.ai_draft = result['draft_content']
            application.status = 'preparing'  # Move to preparing status
            if result.get('amount_requested'):
                application.amount_requested = result['amount_requested']
        else:
            # Create new application with the draft
            application = GrantApplication(
                project_id=request.project_id,
                funding_program_id=request.funding_program_id,
                status='preparing',
                ai_draft=result['draft_content'],
                amount_requested=result.get('amount_requested')
            )
            db.add(application)

        db.commit()
        db.refresh(application)

        return {
            "success": True,
            "draft_content": result['draft_content'],
            "project_id": result['project_id'],
            "funding_program_id": result['program_id'],
            "project_title": result['project_title'],
            "program_name": result['program_name'],
            "amount_requested": result['amount_requested'],
            "application_id": application.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du brouillon: {str(e)}"
        )


# ============================================
# LIST ALL APPLICATIONS
# ============================================

@router.get("/applications")
def list_all_grant_applications(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List grant applications with optional filters.

    Query params:
    - project_id: Filter by project
    - status: Filter by status (draft, submitted, etc.)
    - limit: Max results (default 50)
    """
    query = db.query(GrantApplication)

    if project_id:
        query = query.filter(GrantApplication.project_id == project_id)

    if status:
        query = query.filter(GrantApplication.status == status)

    applications = query.order_by(GrantApplication.created_at.desc()).limit(limit).all()

    result = []
    for app in applications:
        program = db.query(FundingProgram).filter(
            FundingProgram.id == app.funding_program_id
        ).first()

        project = db.query(ProjectInstance).filter(
            ProjectInstance.id == app.project_id
        ).first()

        result.append({
            'id': app.id,
            'project_id': app.project_id,
            'project_title': project.project_data.get('title') if project and project.project_data else None,
            'funding_program_id': app.funding_program_id,
            'program_name': program.name if program else 'Programme inconnu',
            'program_organization': program.organization if program else None,
            'status': app.status,
            'amount_requested': app.amount_requested,
            'amount_approved': app.amount_approved,
            'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None,
            'created_at': app.created_at.isoformat() if app.created_at else None,
            'updated_at': app.updated_at.isoformat() if app.updated_at else None
        })

    return {
        'count': len(result),
        'applications': result
    }


# ============================================
# CREATE APPLICATION
# ============================================

@router.post("/applications", status_code=201)
def create_grant_application(
    request: GrantApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new grant application.

    The application starts in 'draft' status by default.
    """
    # Verify project exists
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == request.project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")

    # Verify program exists
    program = db.query(FundingProgram).filter(
        FundingProgram.id == request.funding_program_id
    ).first()

    if not program:
        raise HTTPException(status_code=404, detail="Programme de financement non trouvé")

    # Validate status
    if request.status and request.status not in GrantApplication.VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Statut invalide. Valeurs acceptées: {', '.join(GrantApplication.VALID_STATUSES)}"
        )

    # Create application
    application = GrantApplication(
        project_id=request.project_id,
        funding_program_id=request.funding_program_id,
        status=request.status or 'draft',
        generated_content=request.generated_content,
        amount_requested=request.amount_requested,
        notes=request.notes
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "success": True,
        "message": "Dossier créé avec succès",
        "application": {
            "id": application.id,
            "project_id": application.project_id,
            "funding_program_id": application.funding_program_id,
            "program_name": program.name,
            "status": application.status,
            "amount_requested": application.amount_requested,
            "created_at": application.created_at.isoformat() if application.created_at else None
        }
    }
