"""
ProjectInstance model - Kanban-style project execution tracking

This model tracks the execution of projects from village_identities.selected_projects
using a 5-stage Kanban workflow:
  exploring → planning → in_progress → completed → abandoned
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any

from app.database import Base


class ProjectInstance(Base):
    """Track execution of village projects (Kanban-style)"""
    __tablename__ = "project_instances"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey('villages.id', ondelete='CASCADE'), nullable=False)
    identity_id = Column(Integer, ForeignKey('village_identities.id', ondelete='SET NULL'))

    # Project data (from generated identity or custom)
    project_data = Column(JSONB, nullable=False)
    # Contains: {title, description, tier, budget_min, budget_max, timeline_months,
    #            difficulty, funding_sources[], inspired_by, first_steps[], case_study}

    # Execution tracking
    status = Column(String(20), default='exploring', index=True)
    # Status values: 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'

    priority = Column(Integer, CheckConstraint('priority >= 1 AND priority <= 5'), default=3)

    # Project details
    notes = Column(Text)  # Mayor's notes about the project
    budget_estimated_min = Column(Integer)  # Euros
    budget_estimated_max = Column(Integer)  # Euros
    budget_actual = Column(Integer)  # Actual spent

    timeline_months = Column(Integer)  # Expected duration
    timeline_actual_months = Column(Integer)  # Actual duration

    # Progress tracking
    completed_steps = Column(ARRAY(Text), default=[])
    next_steps = Column(ARRAY(Text), default=[])

    # Attachments
    attachments = Column(JSONB, default=[])

    # Timestamps
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    abandoned_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    village = relationship("Village", backref="project_instances")
    identity = relationship("VillageIdentity", backref="project_instances")
    grant_applications = relationship("GrantApplication", back_populates="project_instance", cascade="all, delete-orphan")

    # Valid status values
    VALID_STATUSES = ['exploring', 'planning', 'in_progress', 'completed', 'abandoned']

    def __repr__(self):
        title = self.project_data.get('title', 'Untitled') if self.project_data else 'Untitled'
        return f"<ProjectInstance(id={self.id}, title='{title}', status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "village_id": self.village_id,
            "identity_id": self.identity_id,
            "project_data": self.project_data,
            "status": self.status,
            "priority": self.priority,
            "notes": self.notes,
            "budget_estimated_min": self.budget_estimated_min,
            "budget_estimated_max": self.budget_estimated_max,
            "budget_actual": self.budget_actual,
            "timeline_months": self.timeline_months,
            "timeline_actual_months": self.timeline_actual_months,
            "completed_steps": self.completed_steps or [],
            "next_steps": self.next_steps or [],
            "attachments": self.attachments or [],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "abandoned_at": self.abandoned_at.isoformat() if self.abandoned_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
