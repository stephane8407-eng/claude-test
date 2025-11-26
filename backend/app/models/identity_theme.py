from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class IdentityTheme(Base):
    __tablename__ = "identity_themes"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("identity_categories.id"), nullable=False)

    # Core identity
    theme_name = Column(String(100), nullable=False)
    theme_name_fr = Column(String(100))
    tagline = Column(String(200))
    tagline_fr = Column(String(200))

    # AI-generated content
    story_markdown = Column(Text, nullable=False)
    impact_summary = Column(Text)

    # Evidence
    evidence_conflicts = Column(ARRAY(Integer))
    evidence_pois = Column(ARRAY(Integer))
    evidence_data = Column(JSONB)

    # Projects
    project_ideas = Column(JSONB)

    # Metadata
    confidence_score = Column(DECIMAL(3, 2))
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # AI tracking
    ai_model = Column(String(50))
    ai_prompt_version = Column(String(20))
    generated_at = Column(TIMESTAMP, default=func.now())
    reviewed_by_human = Column(Boolean, default=False)
    human_edits_made = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    village = relationship("Village", back_populates="identity_themes")
    category = relationship("IdentityCategory", back_populates="identity_themes")

    def to_dict(self):
        return {
            "id": self.id,
            "village_id": self.village_id,
            "village_slug": self.village.slug if self.village else None,
            "category": self.category.to_dict() if self.category else None,
            "theme_name": self.theme_name,
            "theme_name_fr": self.theme_name_fr,
            "tagline": self.tagline,
            "tagline_fr": self.tagline_fr,
            "story_markdown": self.story_markdown,
            "impact_summary": self.impact_summary,
            "evidence_conflicts": self.evidence_conflicts or [],
            "evidence_pois": self.evidence_pois or [],
            "evidence_data": self.evidence_data or {},
            "project_ideas": self.project_ideas or [],
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "ai_model": self.ai_model,
            "ai_prompt_version": self.ai_prompt_version,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "reviewed_by_human": self.reviewed_by_human,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
