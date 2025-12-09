"""
Projects API - CRUD endpoints for village development initiatives
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.project import Project
from app.models.village import Village


router = APIRouter(prefix="/api/projects", tags=["projects"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    settlement_id: int
    title: str
    short_description: Optional[str] = None
    status: Optional[str] = 'idea'
    themes: Optional[List[str]] = None
    source: Optional[str] = 'manual'
    priority: Optional[int] = 0
    estimated_budget: Optional[str] = None
    estimated_roi: Optional[str] = None
    notes: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    status: Optional[str] = None
    themes: Optional[List[str]] = None
    priority: Optional[int] = None
    estimated_budget: Optional[str] = None
    estimated_roi: Optional[str] = None
    notes: Optional[str] = None


# ============================================================================
# Project Endpoints
# ============================================================================

@router.get("/", response_model=dict)
def list_projects(
    settlement_id: Optional[int] = Query(None, description="Filter by settlement"),
    village_slug: Optional[str] = Query(None, description="Filter by village slug"),
    status: Optional[str] = Query(None, description="Filter by status"),
    source: Optional[str] = Query(None, description="Filter by source"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List projects with optional filters.

    - **settlement_id**: Filter by settlement ID
    - **village_slug**: Filter by village slug
    - **status**: Filter by status (idea, planned, in_progress, completed)
    - **source**: Filter by source (ai_suggested, manual)
    - **theme**: Filter by theme tag
    """
    query = db.query(Project)

    # Handle village_slug filter
    if village_slug:
        village = db.query(Village).filter(Village.slug == village_slug).first()
        if not village:
            raise HTTPException(status_code=404, detail=f"Village '{village_slug}' not found")
        settlement_id = village.id

    if settlement_id:
        query = query.filter(Project.settlement_id == settlement_id)

    if status:
        if status not in Project.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {Project.VALID_STATUSES}"
            )
        query = query.filter(Project.status == status)

    if source:
        if source not in Project.VALID_SOURCES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source. Must be one of: {Project.VALID_SOURCES}"
            )
        query = query.filter(Project.source == source)

    if theme:
        query = query.filter(Project.themes.contains([theme]))

    total = query.count()
    projects = query.order_by(Project.priority.desc(), Project.created_at.desc())\
        .offset(offset).limit(limit).all()

    return {
        "results": [p.to_dict() for p in projects],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{project_id}", response_model=dict)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a single project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return project.to_dict(include_settlement=True)


@router.post("/", response_model=dict, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_village_admin)
):
    """
    Create a new project.

    Requires village_admin role for the settlement.
    """
    # Validate settlement exists
    settlement = db.query(Village).filter(Village.id == project_data.settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail=f"Settlement {project_data.settlement_id} not found")

    # Validate status
    if project_data.status and project_data.status not in Project.VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {Project.VALID_STATUSES}"
        )

    # Validate source
    if project_data.source and project_data.source not in Project.VALID_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source. Must be one of: {Project.VALID_SOURCES}"
        )

    project = Project(
        settlement_id=project_data.settlement_id,
        title=project_data.title,
        short_description=project_data.short_description,
        status=project_data.status or 'idea',
        themes=project_data.themes,
        source=project_data.source or 'manual',
        priority=project_data.priority or 0,
        estimated_budget=project_data.estimated_budget,
        estimated_roi=project_data.estimated_roi,
        notes=project_data.notes
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project.to_dict(include_settlement=True)


@router.put("/{project_id}", response_model=dict)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_village_admin)
):
    """
    Update a project.

    Requires village_admin role for the settlement.
    Note: source field cannot be updated (it's read-only).
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Validate status if provided
    if project_data.status is not None:
        if project_data.status not in Project.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {Project.VALID_STATUSES}"
            )
        project.status = project_data.status

    # Update fields if provided
    if project_data.title is not None:
        project.title = project_data.title
    if project_data.short_description is not None:
        project.short_description = project_data.short_description
    if project_data.themes is not None:
        project.themes = project_data.themes
    if project_data.priority is not None:
        project.priority = project_data.priority
    if project_data.estimated_budget is not None:
        project.estimated_budget = project_data.estimated_budget
    if project_data.estimated_roi is not None:
        project.estimated_roi = project_data.estimated_roi
    if project_data.notes is not None:
        project.notes = project_data.notes

    db.commit()
    db.refresh(project)

    return project.to_dict(include_settlement=True)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_village_admin)
):
    """
    Delete a project.

    Requires village_admin role for the settlement.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    db.delete(project)
    db.commit()

    return None


# ============================================================================
# Village-scoped Endpoints
# ============================================================================

@router.get("/village/{village_slug}", response_model=dict)
def list_village_projects(
    village_slug: str,
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all projects for a specific village.

    Convenience endpoint for village admin dashboards.
    """
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{village_slug}' not found")

    query = db.query(Project).filter(Project.settlement_id == village.id)

    if status:
        if status not in Project.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {Project.VALID_STATUSES}"
            )
        query = query.filter(Project.status == status)

    total = query.count()
    projects = query.order_by(Project.priority.desc(), Project.created_at.desc())\
        .offset(offset).limit(limit).all()

    return {
        "results": [p.to_dict() for p in projects],
        "total": total,
        "village": village.to_dict(),
        "limit": limit,
        "offset": offset
    }


@router.post("/village/{village_slug}", response_model=dict, status_code=201)
def create_village_project(
    village_slug: str,
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
    # TODO: Add auth dependency: current_user = Depends(require_village_admin)
):
    """
    Create a project for a specific village.

    Convenience endpoint that auto-populates settlement_id.
    """
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail=f"Village '{village_slug}' not found")

    # Override settlement_id with village ID
    project_data.settlement_id = village.id

    # Validate status
    if project_data.status and project_data.status not in Project.VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {Project.VALID_STATUSES}"
        )

    project = Project(
        settlement_id=village.id,
        title=project_data.title,
        short_description=project_data.short_description,
        status=project_data.status or 'idea',
        themes=project_data.themes,
        source=project_data.source or 'manual',
        priority=project_data.priority or 0,
        estimated_budget=project_data.estimated_budget,
        estimated_roi=project_data.estimated_roi,
        notes=project_data.notes
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project.to_dict(include_settlement=True)
