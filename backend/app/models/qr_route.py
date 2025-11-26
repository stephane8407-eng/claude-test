"""
QR Route model for tourism walking routes
Links multiple POIs into a guided tourism experience
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
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
    description = Column(Text, nullable=True)

    # POI sequence (JSON array of POI IDs in route order)
    # Example: [1, 5, 3, 7] - visit POIs in this order
    poi_ids = Column(JSON, nullable=False)

    # Route metadata
    estimated_duration_minutes = Column(Integer, nullable=True)  # Estimated time to complete
    distance_meters = Column(Integer, nullable=True)  # Total route distance

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
