"""
GrantApplication model - Track grant applications for project instances

Tracks the lifecycle of grant applications:
  draft → submitted → under_review → approved/rejected/abandoned
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any

from app.database import Base


class GrantApplication(Base):
    """Track grant applications for project instances"""
    __tablename__ = "grant_applications"

    id = Column(Integer, primary_key=True, index=True)
    project_instance_id = Column(Integer, ForeignKey('project_instances.id', ondelete='CASCADE'), nullable=False)
    funding_program_id = Column(Integer, ForeignKey('funding_programs.id', ondelete='SET NULL'))

    # Application status
    status = Column(String(50), default='draft', index=True)
    # Status values: 'draft', 'submitted', 'under_review', 'approved', 'rejected', 'abandoned'

    # Generated content (from Claude API)
    generated_content = Column(Text)  # Full application text

    # Submission details
    amount_requested = Column(Integer)  # Euros
    amount_approved = Column(Integer)  # Euros (if approved)

    submitted_date = Column(Date)
    decision_date = Column(Date)
    decision_notes = Column(Text)

    # Documents
    documents = Column(JSONB, default=[])
    # Array of: {filename, url, mime_type, size, uploaded_at, doc_type}

    # Notes
    notes = Column(Text)  # Internal notes about the application

    # Timestamps
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    project_instance = relationship("ProjectInstance", back_populates="grant_applications")
    funding_program = relationship("FundingProgram", back_populates="grant_applications")

    # Valid status values
    VALID_STATUSES = ['draft', 'submitted', 'under_review', 'approved', 'rejected', 'abandoned']

    def __repr__(self):
        return f"<GrantApplication(id={self.id}, project_instance_id={self.project_instance_id}, status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "project_instance_id": self.project_instance_id,
            "funding_program_id": self.funding_program_id,
            "status": self.status,
            "generated_content": self.generated_content,
            "amount_requested": self.amount_requested,
            "amount_approved": self.amount_approved,
            "submitted_date": self.submitted_date.isoformat() if self.submitted_date else None,
            "decision_date": self.decision_date.isoformat() if self.decision_date else None,
            "decision_notes": self.decision_notes,
            "documents": self.documents or [],
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
