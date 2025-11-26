"""
Battle model - LAYER 0: Historical battles across FR, UK, BE
"""
from sqlalchemy import Column, Integer, String, Date, DECIMAL, ARRAY, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base


class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    war_period = Column(String(100), index=True)  # WW1, WW2, Napoleonic, etc.
    start_date = Column(Date)
    end_date = Column(Date)
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    country = Column(String(2), index=True)  # FR, UK, BE
    sides_involved = Column(ARRAY(Text))  # ["Allies", "Axis"]
    outcome = Column(String(50))  # "Allied victory", etc.
    significance = Column(String(20), index=True)  # minor, moderate, major
    casualties_estimated = Column(Integer)
    sources = Column(ARRAY(Text))  # URLs
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # PostGIS geometry column (automatically created by index in schema)
    # We'll use lat/lng directly in queries with ST_MakePoint

    # Week 10: QR Code relationship
    qr_codes = relationship("QRCode", back_populates="battle")

    def __repr__(self):
        return f"<Battle(id={self.id}, name='{self.name}', period='{self.war_period}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "war_period": self.war_period,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "country": self.country,
            "sides_involved": self.sides_involved,
            "outcome": self.outcome,
            "significance": self.significance,
            "casualties_estimated": self.casualties_estimated,
            "sources": self.sources,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
