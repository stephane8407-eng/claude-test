from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base

class POI(Base):
    __tablename__ = "pois"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Multi-tenancy: POIs belong to a village
    village_id = Column(Integer, ForeignKey('villages.id', ondelete='CASCADE'), nullable=False, index=True)

    # POI type
    poi_type_id = Column(Integer, ForeignKey('poi_types.id'), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Location
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    address = Column(Text)

    # Additional attributes (flexible JSON)
    attributes = Column(JSONB, default={})

    # Visibility & status
    is_public = Column(Boolean, default=True, index=True)
    status = Column(String(20), default='active', index=True)

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by_user_id = Column(Integer)

    # Source information
    source = Column(String(100))
    source_url = Column(Text)

    # Relationships
    # village = relationship("Village", back_populates="pois")
    # poi_type = relationship("POIType", back_populates="pois")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'village_id': self.village_id,
            'poi_type_id': self.poi_type_id,
            'name': self.name,
            'description': self.description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'address': self.address,
            'attributes': self.attributes or {},
            'is_public': self.is_public,
            'status': self.status,
            'source': self.source,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<POI(id={self.id}, name='{self.name}', village_id={self.village_id}, type_id={self.poi_type_id})>"
