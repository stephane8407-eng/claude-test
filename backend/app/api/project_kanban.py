"""
Project Kanban API - Endpoints for Phase E Project Management Dashboard

Provides Kanban-style project tracking with 5 stages:
  exploring → planning → in_progress → completed → abandoned
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.project_instance import ProjectInstance
from app.models.village_identity import VillageIdentity
from app.models.village import Village
from app.models.grant_application import GrantApplication


router = APIRouter(prefix="/api/villages", tags=["project-kanban"])


# ============================================
# PYDANTIC SCHEMAS (Request/Response models)
# ============================================

class ProjectInstanceCreate(BaseModel):
    """Create a project instance from village identity or custom"""
    identity_id: Optional[int] = None  # If from village identity
    project_index: Optional[int] = None  # Which project from the identity's selected_projects
    project_data: Optional[dict] = None  # Custom project data (if not from identity)
    priority: Optional[int] = 3
    notes: Optional[str] = None


class ProjectInstanceUpdate(BaseModel):
    """Update project instance details"""
    status: Optional[str] = None
    priority: Optional[int] = None
    notes: Optional[str] = None
    budget_actual: Optional[int] = None
    timeline_actual_months: Optional[int] = None
    completed_steps: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    # Phase E Week 2.5: Enhanced project data fields
    budget_estimated_min: Optional[int] = None
    budget_estimated_max: Optional[int] = None
    timeline_months: Optional[int] = None
    project_data: Optional[dict] = None  # JSONB field for all extended data


class ProjectStatusUpdate(BaseModel):
    """Quick status change for drag-and-drop"""
    status: str  # 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'


# ============================================
# KANBAN PROJECT ENDPOINTS
# ============================================

@router.post("/{village_slug}/projects")
def create_kanban_project(
    village_slug: str,
    project_create: ProjectInstanceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a project instance for Kanban tracking.

    Can create from:
    1. A village identity's selected_projects (provide identity_id + project_index)
    2. Custom project data (provide project_data directly)
    """
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    project_data = None
    identity_id = None
    budget_min = None
    budget_max = None
    timeline = 12

    # Option 1: Create from village identity
    if project_create.identity_id is not None and project_create.project_index is not None:
        identity = db.query(VillageIdentity).filter(
            VillageIdentity.id == project_create.identity_id,
            VillageIdentity.village_id == village.id
        ).first()

        if not identity:
            raise HTTPException(status_code=404, detail="Village identity not found")

        selected_projects = identity.selected_projects or []
        if project_create.project_index < 0 or project_create.project_index >= len(selected_projects):
            raise HTTPException(status_code=400, detail=f"Invalid project index. Available: 0-{len(selected_projects)-1}")

        project_data = selected_projects[project_create.project_index]
        identity_id = identity.id

        # Extract budget and timeline from project data
        budget_min = project_data.get('budget_min') or project_data.get('budgetMin', 0)
        budget_max = project_data.get('budget_max') or project_data.get('budgetMax', 0)
        timeline = project_data.get('timeline_months') or project_data.get('timelineMonths', 12)

    # Option 2: Custom project data
    elif project_create.project_data:
        project_data = project_create.project_data
        budget_min = project_data.get('budget_min', 0)
        budget_max = project_data.get('budget_max', 0)
        timeline = project_data.get('timeline_months', 12)
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either (identity_id + project_index) or project_data"
        )

    # Create project instance
    project = ProjectInstance(
        village_id=village.id,
        identity_id=identity_id,
        project_data=project_data,
        status='exploring',
        priority=project_create.priority or 3,
        notes=project_create.notes,
        budget_estimated_min=budget_min,
        budget_estimated_max=budget_max,
        timeline_months=timeline,
        next_steps=project_data.get('first_steps') or project_data.get('firstSteps', [])
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "message": "Project instance created successfully",
        "project": project.to_dict()
    }


@router.get("/{village_slug}/projects")
def list_kanban_projects(
    village_slug: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all project instances for a village's Kanban board.

    Returns projects grouped by status for easy Kanban rendering.

    Optional filters:
    - status: 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'
    """
    # Get village
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    # Build query
    query = db.query(ProjectInstance).filter(ProjectInstance.village_id == village.id)

    if status:
        if status not in ProjectInstance.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {ProjectInstance.VALID_STATUSES}"
            )
        query = query.filter(ProjectInstance.status == status)

    projects = query.order_by(
        ProjectInstance.priority.desc(),
        ProjectInstance.created_at.desc()
    ).all()

    # Group by status for Kanban board
    by_status = {
        'exploring': [],
        'planning': [],
        'in_progress': [],
        'completed': [],
        'abandoned': []
    }

    for project in projects:
        by_status[project.status].append(project.to_dict())

    return {
        "village": {
            "id": village.id,
            "name": village.name,
            "slug": village_slug
        },
        "projects": [p.to_dict() for p in projects],
        "by_status": by_status,
        "counts": {
            "total": len(projects),
            "exploring": len(by_status['exploring']),
            "planning": len(by_status['planning']),
            "in_progress": len(by_status['in_progress']),
            "completed": len(by_status['completed']),
            "abandoned": len(by_status['abandoned'])
        }
    }


@router.get("/{village_slug}/projects/{project_id}")
def get_kanban_project(
    village_slug: str,
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific project instance."""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project instance not found")

    # Include related grant applications
    grant_apps = db.query(GrantApplication).filter(
        GrantApplication.project_instance_id == project.id
    ).all()

    project_dict = project.to_dict()
    project_dict['grant_applications'] = [app.to_dict() for app in grant_apps]

    return project_dict


@router.put("/{village_slug}/projects/{project_id}")
def update_kanban_project(
    village_slug: str,
    project_id: int,
    project_update: ProjectInstanceUpdate,
    db: Session = Depends(get_db)
):
    """Update project instance details."""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project instance not found")

    # Update fields
    if project_update.status is not None:
        if project_update.status not in ProjectInstance.VALID_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {ProjectInstance.VALID_STATUSES}"
            )
        project.status = project_update.status

        # Set timestamp based on status
        if project_update.status == 'in_progress' and not project.started_at:
            project.started_at = datetime.now()
        elif project_update.status == 'completed' and not project.completed_at:
            project.completed_at = datetime.now()
        elif project_update.status == 'abandoned' and not project.abandoned_at:
            project.abandoned_at = datetime.now()

    if project_update.priority is not None:
        project.priority = project_update.priority

    if project_update.notes is not None:
        project.notes = project_update.notes

    if project_update.budget_actual is not None:
        project.budget_actual = project_update.budget_actual

    if project_update.timeline_actual_months is not None:
        project.timeline_actual_months = project_update.timeline_actual_months

    if project_update.completed_steps is not None:
        project.completed_steps = project_update.completed_steps

    if project_update.next_steps is not None:
        project.next_steps = project_update.next_steps

    # Phase E Week 2.5: Handle budget and timeline fields
    if project_update.budget_estimated_min is not None:
        project.budget_estimated_min = project_update.budget_estimated_min

    if project_update.budget_estimated_max is not None:
        project.budget_estimated_max = project_update.budget_estimated_max

    if project_update.timeline_months is not None:
        project.timeline_months = project_update.timeline_months

    # Handle project_data JSONB field (merge with existing data)
    if project_update.project_data is not None:
        existing_data = project.project_data or {}
        # Merge new data with existing, new values override
        merged_data = {**existing_data, **project_update.project_data}
        project.project_data = merged_data

    project.updated_at = datetime.now()

    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "message": "Project instance updated successfully",
        "project": project.to_dict()
    }


@router.put("/{village_slug}/projects/{project_id}/status")
def update_kanban_project_status(
    village_slug: str,
    project_id: int,
    status_update: ProjectStatusUpdate,
    db: Session = Depends(get_db)
):
    """Quick status update for Kanban drag-and-drop."""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project instance not found")

    # Validate status
    if status_update.status not in ProjectInstance.VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(ProjectInstance.VALID_STATUSES)}"
        )

    project.status = status_update.status

    # Set timestamps
    if status_update.status == 'in_progress' and not project.started_at:
        project.started_at = datetime.now()
    elif status_update.status == 'completed' and not project.completed_at:
        project.completed_at = datetime.now()
    elif status_update.status == 'abandoned' and not project.abandoned_at:
        project.abandoned_at = datetime.now()

    project.updated_at = datetime.now()

    db.commit()
    db.refresh(project)

    return {
        "success": True,
        "message": f"Project status changed to {status_update.status}",
        "project": project.to_dict()
    }


@router.delete("/{village_slug}/projects/{project_id}")
def delete_kanban_project(
    village_slug: str,
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete a project instance."""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project instance not found")

    db.delete(project)
    db.commit()

    return {
        "success": True,
        "message": "Project instance deleted successfully"
    }


# ============================================
# PROJECT STATISTICS
# ============================================

@router.get("/{village_slug}/projects/stats")
def get_kanban_stats(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get project statistics for analytics dashboard."""
    village = db.query(Village).filter(Village.slug == village_slug).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    projects = db.query(ProjectInstance).filter(
        ProjectInstance.village_id == village.id
    ).all()

    # Calculate stats
    total = len(projects)
    by_status = {}
    total_budget_estimated = 0
    total_budget_actual = 0

    for project in projects:
        # Count by status
        status = project.status
        by_status[status] = by_status.get(status, 0) + 1

        # Sum budgets
        if project.budget_estimated_min and project.budget_estimated_max:
            avg_estimated = (project.budget_estimated_min + project.budget_estimated_max) / 2
            total_budget_estimated += avg_estimated

        if project.budget_actual:
            total_budget_actual += project.budget_actual

    return {
        "village": {
            "id": village.id,
            "name": village.name,
            "slug": village_slug
        },
        "total_projects": total,
        "by_status": by_status,
        "budget": {
            "total_estimated": int(total_budget_estimated),
            "total_actual": total_budget_actual,
            "percentage_spent": round((total_budget_actual / total_budget_estimated * 100), 2) if total_budget_estimated > 0 else 0
        }
    }
