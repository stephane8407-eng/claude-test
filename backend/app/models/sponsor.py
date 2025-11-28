"""
Sponsor model - Partners and advertisers
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    short_description = Column(Text)
    type = Column(String(50), nullable=False, index=True)  # 'local_business', 'regional_partner', 'founding_partner'
    sector = Column(String(100), index=True)  # 'real_estate', 'bank', 'tourism', 'eco', etc.
    regions = Column(ARRAY(Text))  # Administrative regions or free tags
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    slots = relationship("SponsorSlot", back_populates="sponsor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sponsor(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self, include_slots=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "logo_url": self.logo_url,
            "website_url": self.website_url,
            "short_description": self.short_description,
            "type": self.type,
            "sector": self.sector,
            "regions": self.regions or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_slots:
            data["slots"] = [slot.to_dict() for slot in self.slots]

        return data
