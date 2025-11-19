"""
Place model - LAYER 1: Villages, towns, communes
"""
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    country = Column(String(2), nullable=False, index=True)  # FR, UK, BE
    admin_code = Column(String(20))  # INSEE, ONS, Statbel code
    centroid_lat = Column(DECIMAL(10, 7), nullable=False)
    centroid_lng = Column(DECIMAL(10, 7), nullable=False)
    population = Column(Integer)
    area_km2 = Column(DECIMAL(10, 2))
    depth_level = Column(String(20), server_default='light', index=True)  # light, partner, flagship
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship to place_contexts
    context = relationship("PlaceContext", back_populates="place", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Place(id={self.id}, name='{self.name}', country='{self.country}')>"

    def to_dict(self, include_context=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "admin_code": self.admin_code,
            "centroid_lat": float(self.centroid_lat) if self.centroid_lat else None,
            "centroid_lng": float(self.centroid_lng) if self.centroid_lng else None,
            "population": self.population,
            "area_km2": float(self.area_km2) if self.area_km2 else None,
            "depth_level": self.depth_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_context and self.context:
            data["context"] = self.context.to_dict()

        return data
