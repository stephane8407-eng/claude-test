# backend/app/api/projects.py
"""
FastAPI endpoints for Phase E: Project Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import func

from app.database import get_db
from app.models.project import ProjectInstance, VillageIdentity, FundingProgram, GrantApplication
from app.models import Place  # Assuming Place model exists

router = APIRouter(tags=["Projects"])

# ============================================
# PYDANTIC SCHEMAS (Request/Response models)
# ============================================

class ProjectCreate(BaseModel):
    """Create a project from generated identity"""
    identity_id: int
    project_index: int  # Which project from the identity's projects array (0-5)
    priority: Optional[int] = 3
    notes: Optional[str] = None

class ProjectUpdate(BaseModel):
    """Update project details"""
    status: Optional[str] = None
    priority: Optional[int] = None
    notes: Optional[str] = None
    budget_actual: Optional[int] = None
    timeline_actual_months: Optional[int] = None
    completed_steps: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None

class ProjectStatusUpdate(BaseModel):
    """Quick status change"""
    status: str  # 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'

# ============================================
# PROJECT ENDPOINTS
# ============================================

@router.post("/api/villages/{village_slug}/projects")
def create_project(
    village_slug: str,
    project_create: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a project instance from a generated identity
    
    This saves a specific project from the identity's projects array
    into project_instances table for tracking.
    """
    # Get village
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    # Get identity
    identity = db.query(VillageIdentity).filter(
        VillageIdentity.id == project_create.identity_id,
        VillageIdentity.village_id == village.id
    ).first()
    
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    # Get the specific project from the identity's projects array
    if project_create.project_index < 0 or project_create.project_index >= len(identity.projects):
        raise HTTPException(status_code=400, detail="Invalid project index")
    
    project_data = identity.projects[project_create.project_index]
    
    # Extract budget and timeline from project data
    budget_min = project_data.get('budget_min', 0)
    budget_max = project_data.get('budget_max', 0)
    timeline = project_data.get('timeline_months', 12)
    
    # Create project instance
    project = ProjectInstance(
        village_id=village.id,
        identity_id=identity.id,
        project_data=project_data,
        status='exploring',
        priority=project_create.priority,
        notes=project_create.notes,
        budget_estimated_min=budget_min,
        budget_estimated_max=budget_max,
        timeline_months=timeline,
        next_steps=project_data.get('first_steps', [])
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return {
        "success": True,
        "message": "Project created successfully",
        "project": project.to_dict()
    }


@router.get("/api/villages/{village_slug}/projects")
def list_projects(
    village_slug: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all projects for a village
    
    Optional filters:
    - status: 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'
    """
    # Get village
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    # Build query
    query = db.query(ProjectInstance).filter(ProjectInstance.village_id == village.id)
    
    if status:
        query = query.filter(ProjectInstance.status == status)
    
    projects = query.order_by(ProjectInstance.priority.desc(), ProjectInstance.created_at.desc()).all()
    
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


@router.get("/api/villages/{village_slug}/projects/{project_id}")
def get_project(
    village_slug: str,
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific project"""
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Include related grant applications
    grant_apps = db.query(GrantApplication).filter(
        GrantApplication.project_id == project.id
    ).all()
    
    project_dict = project.to_dict()
    project_dict['grant_applications'] = [app.to_dict() for app in grant_apps]
    
    return project_dict


@router.put("/api/villages/{village_slug}/projects/{project_id}")
def update_project(
    village_slug: str,
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project details"""
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    if project_update.status is not None:
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
    
    project.updated_at = datetime.now()
    
    db.commit()
    db.refresh(project)
    
    return {
        "success": True,
        "message": "Project updated successfully",
        "project": project.to_dict()
    }


@router.put("/api/villages/{village_slug}/projects/{project_id}/status")
def update_project_status(
    village_slug: str,
    project_id: int,
    status_update: ProjectStatusUpdate,
    db: Session = Depends(get_db)
):
    """Quick status update (for Kanban drag-and-drop)"""
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate status
    valid_statuses = ['exploring', 'planning', 'in_progress', 'completed', 'abandoned']
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
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


@router.delete("/api/villages/{village_slug}/projects/{project_id}")
def delete_project(
    village_slug: str,
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete a project"""
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    
    project = db.query(ProjectInstance).filter(
        ProjectInstance.id == project_id,
        ProjectInstance.village_id == village.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return {
        "success": True,
        "message": "Project deleted successfully"
    }


# ============================================
# PROJECT STATISTICS
# ============================================

@router.get("/api/villages/{village_slug}/projects/stats")
def get_project_stats(
    village_slug: str,
    db: Session = Depends(get_db)
):
    """Get project statistics for analytics dashboard"""
    village = db.query(Place).filter(func.lower(Place.name) == village_slug.lower()).first()
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
        "total_projects": total,
        "by_status": by_status,
        "budget": {
            "total_estimated": int(total_budget_estimated),
            "total_actual": total_budget_actual,
            "percentage_spent": round((total_budget_actual / total_budget_estimated * 100), 2) if total_budget_estimated > 0 else 0
        }
    }
