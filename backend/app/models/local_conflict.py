"""
LocalConflict model - AI-scraped conflict events with 6-category impact framework
"""
from sqlalchemy import Column, Integer, String, Date, DECIMAL, ARRAY, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base


class LocalConflict(Base):
    __tablename__ = "local_conflicts"

    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy
    village_id = Column(Integer, ForeignKey('villages.id'), index=True)

    # Basic Information
    name = Column(String(500), nullable=False)
    date = Column(Date, index=True)
    date_str = Column(String(50))  # Original date string
    date_precision = Column(String(20))  # "day", "month", "year", "circa"
    location = Column(String(500), nullable=False)
    latitude = Column(DECIMAL(10, 7))
    longitude = Column(DECIMAL(10, 7))

    # Conflict Classification
    conflict_type = Column(String(50), index=True)  # battle, siege, skirmish, etc.
    period = Column(String(50), index=True)  # ancient, medieval, ww1, ww2, etc.
    duration = Column(String(100))

    # Participants & Outcome
    participants = Column(JSONB)  # [{name, side, role}, ...]
    casualties = Column(JSONB)  # {side1, side2, civilians} or "unknown"
    outcome = Column(Text)

    # Context & Analysis
    strategic_importance = Column(Text)
    preceding_events = Column(Text)
    consequences = Column(Text)

    # 6-Category Impact Framework
    impact_today = Column(JSONB)  # {infrastructure, economy, identity, demographics, governance, tourism}

    # Metadata
    sources = Column(ARRAY(Text))  # Source descriptions
    confidence_score = Column(Integer, index=True)  # 0-100

    # Scraping Metadata
    scraper_location_name = Column(String(255))
    scraper_department = Column(String(255))
    scraper_region = Column(String(255))
    scraper_timestamp = Column(TIMESTAMP)
    scraper_radius_km = Column(DECIMAL(6, 2))

    # Foreign Key
    place_id = Column(Integer, ForeignKey('places.id', ondelete='SET NULL'), index=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LocalConflict(id={self.id}, name='{self.name}', date='{self.date}', type='{self.conflict_type}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "village_id": self.village_id,
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "date_str": self.date_str,
            "date_precision": self.date_precision,
            "location": self.location,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "conflict_type": self.conflict_type,
            "period": self.period,
            "duration": self.duration,
            "participants": self.participants,
            "casualties": self.casualties,
            "outcome": self.outcome,
            "strategic_importance": self.strategic_importance,
            "preceding_events": self.preceding_events,
            "consequences": self.consequences,
            "impact_today": self.impact_today,
            "sources": self.sources,
            "confidence_score": self.confidence_score,
            "scraper_location_name": self.scraper_location_name,
            "scraper_department": self.scraper_department,
            "scraper_region": self.scraper_region,
            "scraper_timestamp": self.scraper_timestamp.isoformat() if self.scraper_timestamp else None,
            "scraper_radius_km": float(self.scraper_radius_km) if self.scraper_radius_km else None,
            "place_id": self.place_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
