"""
Topic model - SEO landing pages for theme-based discovery
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    short_description = Column(Text)
    long_description = Column(Text)  # 300-800 words for SEO
    hero_image_url = Column(String(500))
    tags = Column(ARRAY(Text))  # For auto-association with entities

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    sponsor_slots = relationship(
        "SponsorSlot",
        primaryjoin="and_(Topic.id==foreign(SponsorSlot.object_id), SponsorSlot.object_type=='topic')",
        viewonly=True
    )

    def __repr__(self):
        return f"<Topic(id={self.id}, slug='{self.slug}', title='{self.title}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "short_description": self.short_description,
            "long_description": self.long_description,
            "hero_image_url": self.hero_image_url,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
