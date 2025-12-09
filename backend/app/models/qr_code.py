"""
QR Code model for trackable tourism QR codes
Enables villages to create and track QR codes for POIs and routes
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class QRCode(Base):
    """
    QR code for tourism tracking and monetization

    Each QR code can be linked to:
    - A village (required)
    - A POI (optional)
    - A battle (optional)
    - A tourism route (optional)
    """
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=False, index=True)
    poi_id = Column(Integer, ForeignKey("pois.id"), nullable=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), nullable=True, index=True)
    route_id = Column(Integer, ForeignKey("qr_routes.id"), nullable=True, index=True)

    # QR code identifier (unique short code, e.g., "spv-chirac-001")
    code = Column(String(50), unique=True, nullable=False, index=True)

    # QR code metadata
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Target URL (where the QR code redirects)
    target_url = Column(Text, nullable=False)

    # Stored QR code image URL (path to generated image)
    qr_image_url = Column(Text, nullable=True)

    # Tracking
    scan_count = Column(Integer, default=0, nullable=False)
    last_scanned_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    village = relationship("Village", back_populates="qr_codes")
    poi = relationship("POI", back_populates="qr_codes")
    battle = relationship("Battle", back_populates="qr_codes")
    route = relationship("QRRoute", back_populates="qr_codes")
    scans = relationship("QRScan", back_populates="qr_code", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QRCode(id={self.id}, code={self.code}, village={self.village_id})>"
