"""
Project model - AI-suggested and manual village development initiatives
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(Integer, ForeignKey('villages.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    short_description = Column(Text)
    status = Column(String(50), default='idea', index=True)  # 'idea', 'planned', 'in_progress', 'completed'
    themes = Column(ARRAY(Text))
    source = Column(String(50), default='manual', index=True)  # 'ai_suggested', 'manual'
    priority = Column(Integer, default=0)  # Higher = more important
    estimated_budget = Column(String(100))  # e.g., "€2,000-5,000"
    estimated_roi = Column(String(100))  # e.g., "€8,000/year"
    notes = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    settlement = relationship("Village", backref="projects")

    # Valid status values
    VALID_STATUSES = ['idea', 'planned', 'in_progress', 'completed']
    VALID_SOURCES = ['ai_suggested', 'manual']

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', status='{self.status}')>"

    def to_dict(self, include_settlement=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "settlement_id": self.settlement_id,
            "title": self.title,
            "short_description": self.short_description,
            "status": self.status,
            "themes": self.themes or [],
            "source": self.source,
            "priority": self.priority,
            "estimated_budget": self.estimated_budget,
            "estimated_roi": self.estimated_roi,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_settlement and self.settlement:
            data["settlement"] = {
                "id": self.settlement.id,
                "name": self.settlement.name,
                "slug": self.settlement.slug,
            }

        return data
