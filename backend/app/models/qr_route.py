"""
QR Route model for tourism walking routes
Links multiple POIs into a guided tourism experience
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, ARRAY, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class QRRoute(Base):
    """
    Tourism route linking multiple POIs

    Allows villages to create guided walking tours with multiple stops.
    Each route can have a QR code that links to the full route information.
    """
    __tablename__ = "qr_routes"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)

    # Route information
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, index=True)  # V1 Spec
    description = Column(Text, nullable=True)

    # V1 Spec: New fields
    hero_image_url = Column(String(500))  # Hero image for route detail page
    gpx_url = Column(String(500))  # URL to GPX file
    distance_km = Column(DECIMAL(5, 2))  # Total route distance in km
    duration_minutes = Column(Integer)  # Estimated time to complete (renamed from estimated_duration_minutes)
    route_type = Column(String(50))  # 'walk', 'hike', 'cycle', 'trail_run'
    school_friendly = Column(Boolean, default=False)  # Suitable for school groups
    themes = Column(ARRAY(Text))  # Array of theme tags
    waypoints = Column(JSONB)  # Array of {lat, lng, name, description, placeId?}

    # Legacy fields (kept for backwards compatibility)
    poi_ids = Column(JSONB)  # JSON array of POI IDs in route order
    distance_meters = Column(Integer, nullable=True)  # Legacy: Total route distance in meters

    # Route difficulty (easy, moderate, hard)
    difficulty = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    village = relationship("Village", back_populates="qr_routes")
    qr_codes = relationship("QRCode", back_populates="route")

    def __repr__(self):
        return f"<QRRoute(id={self.id}, name={self.name}, village={self.village_id})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'village_id': self.village_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            # V1 Spec: New fields
            'hero_image_url': self.hero_image_url,
            'gpx_url': self.gpx_url,
            'distance_km': float(self.distance_km) if self.distance_km else None,
            'duration_minutes': self.duration_minutes,
            'route_type': self.route_type,
            'difficulty': self.difficulty,
            'school_friendly': self.school_friendly,
            'themes': self.themes or [],
            'waypoints': self.waypoints or [],
            # Legacy fields
            'poi_ids': self.poi_ids or [],
            'distance_meters': self.distance_meters,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
