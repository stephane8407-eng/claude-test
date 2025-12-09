"""
VillageIdentity model - Stores AI-generated identity for villages

Stores the identity summary, narrative, themes, and projects
generated through the Identity Audit wizard.
"""
from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class VillageIdentity(Base):
    __tablename__ = "village_identities"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey('villages.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Identity text content
    identity_summary = Column(Text, nullable=False)
    identity_narrative = Column(Text, nullable=False)
    live_here_summary = Column(Text, nullable=False)

    # Selected themes and projects (JSONB arrays)
    selected_themes = Column(JSONB, nullable=False, default=[])
    selected_projects = Column(JSONB, nullable=False, default=[])

    # Publication status
    is_published = Column(Boolean, default=False)
    published_at = Column(TIMESTAMP, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    village = relationship("Village", backref="identity")

    def __repr__(self):
        return f"<VillageIdentity(id={self.id}, village_id={self.village_id}, published={self.is_published})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'village_id': self.village_id,
            'identity_summary': self.identity_summary,
            'identity_narrative': self.identity_narrative,
            'live_here_summary': self.live_here_summary,
            'selected_themes': self.selected_themes or [],
            'selected_projects': self.selected_projects or [],
            'is_published': self.is_published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
