from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship

from app.database import Base

class Village(Base):
    __tablename__ = "villages"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    # Location
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    country = Column(String(2), nullable=False, index=True)
    department = Column(String(100))
    region = Column(String(100))

    # Village details
    population = Column(Integer)
    area_km2 = Column(DECIMAL(10, 2))

    # Subscription
    subscription_tier = Column(String(20), default='free', index=True)
    subscription_status = Column(String(20), default='active', index=True)
    subscription_expires_at = Column(Date)

    # Settings (flexible JSON)
    settings = Column(JSONB, default={})

    # Identity themes (from AI analysis)
    identity_themes = Column(JSONB)

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships (add later when ready)
    # conflicts = relationship("LocalConflict", back_populates="village")
    # places = relationship("Place", back_populates="village")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'country': self.country,
            'department': self.department,
            'region': self.region,
            'population': self.population,
            'area_km2': float(self.area_km2) if self.area_km2 else None,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'settings': self.settings or {},
            'identity_themes': self.identity_themes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Village(id={self.id}, name='{self.name}', tier='{self.subscription_tier}')>"
