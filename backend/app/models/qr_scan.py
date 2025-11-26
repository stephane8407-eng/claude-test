"""
QR Scan model for tracking QR code scans
Records detailed analytics for each scan
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class QRScan(Base):
    """
    Individual QR code scan record

    Tracks each scan with device and location metadata for analytics
    """
    __tablename__ = "qr_scans"

    id = Column(Integer, primary_key=True, index=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False, index=True)

    # Scan metadata
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Device information (parsed from user agent)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(20), nullable=True, index=True)  # mobile, tablet, desktop, bot
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Privacy-compliant tracking
    ip_address_hash = Column(String(64), nullable=True, index=True)  # SHA256 hash of IP
    session_id = Column(String(64), nullable=True, index=True)  # For unique visitor tracking

    # HTTP metadata
    referrer = Column(Text, nullable=True)

    # Geolocation (optional - from IP geolocation service)
    country = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)

    # Relationships
    qr_code = relationship("QRCode", back_populates="scans")

    def __repr__(self):
        return f"<QRScan(id={self.id}, qr_code_id={self.qr_code_id}, device={self.device_type})>"
