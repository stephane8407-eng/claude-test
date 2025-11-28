from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, TIMESTAMP, func, ARRAY
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

    # V1 Spec: Identity fields
    summary_identity = Column(Text)  # Short tagline for public display
    long_identity = Column(Text)  # 1-3 paragraph narrative
    live_here_summary = Column(Text)  # "Living here" section content
    hero_image_url = Column(String(500))  # Hero image for public page
    themes = Column(ARRAY(Text))  # Array of theme tags

    # Subscription
    subscription_tier = Column(String(20), default='free', index=True)
    subscription_status = Column(String(20), default='active', index=True)
    subscription_expires_at = Column(Date)

    # Settings (flexible JSON)
    settings = Column(JSONB, default={})

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships (add later when ready)
    # conflicts = relationship("LocalConflict", back_populates="village")
    # places = relationship("Place", back_populates="village")

    # Week 3: Identity Engine relationships
    identity_themes = relationship("IdentityTheme", back_populates="village")
    data_snapshots = relationship("VillageDataSnapshot", back_populates="village")

    # Week 10: QR Code relationships
    qr_codes = relationship("QRCode", back_populates="village")
    qr_routes = relationship("QRRoute", back_populates="village")

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
            # V1 Spec: Identity fields
            'summary_identity': self.summary_identity,
            'long_identity': self.long_identity,
            'live_here_summary': self.live_here_summary,
            'hero_image_url': self.hero_image_url,
            'themes': self.themes or [],
            # Subscription
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'settings': self.settings or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Village(id={self.id}, name='{self.name}', tier='{self.subscription_tier}')>"
