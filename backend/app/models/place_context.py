"""
PlaceContext model - LAYER 2: AI-generated intelligence about places
"""
from sqlalchemy import Column, Integer, String, Text, ARRAY, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PlaceContext(Base):
    __tablename__ = "place_contexts"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey('places.id', ondelete='CASCADE'), index=True)

    # Processed summaries
    ai_summary = Column(Text)  # 2-3 paragraph overview
    key_events = Column(JSONB)  # [{date, title, description, source}]
    mentioned_units = Column(ARRAY(Text))  # Military units found
    nearby_places = Column(ARRAY(Integer))  # Array of place IDs
    legends_summary = Column(Text)  # Folklore summary
    impact_today = Column(Text)  # Past → Present connection (KEY FEATURE!)

    # Metadata
    sources = Column(ARRAY(Text))  # URLs
    scraping_method = Column(String(20), server_default='ai-led')  # basic, ai-led
    confidence_score = Column(Integer, CheckConstraint('confidence_score >= 0 AND confidence_score <= 100'), index=True)
    raw_intelligence_json = Column(JSONB)  # Full scraper output (260K+ chars)
    last_updated = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationship to place
    place = relationship("Place", back_populates="context")

    def __repr__(self):
        return f"<PlaceContext(id={self.id}, place_id={self.place_id}, confidence={self.confidence_score})>"

    def to_dict(self, include_raw=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "place_id": self.place_id,
            "ai_summary": self.ai_summary,
            "key_events": self.key_events,
            "mentioned_units": self.mentioned_units,
            "nearby_places": self.nearby_places,
            "legends_summary": self.legends_summary,
            "impact_today": self.impact_today,
            "sources": self.sources,
            "scraping_method": self.scraping_method,
            "confidence_score": self.confidence_score,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

        # Only include raw intelligence if explicitly requested
        if include_raw and self.raw_intelligence_json:
            data["raw_intelligence_json"] = self.raw_intelligence_json

        return data
