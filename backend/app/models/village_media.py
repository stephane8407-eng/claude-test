"""
VillageMedia model - Photos, videos, documents uploaded by village admins

Supports automatic geolocation extraction from EXIF data.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any

from app.database import Base


class VillageMedia(Base):
    """Photos, videos, documents uploaded by village admins"""
    __tablename__ = "village_media"

    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey('villages.id', ondelete='CASCADE'), nullable=False)

    # Media type
    media_type = Column(String(20), nullable=False, index=True)  # 'photo', 'video', 'document'
    category = Column(String(50), index=True)  # 'heritage', 'nature', 'community', 'economy', 'events'

    # File details
    url = Column(String(500), nullable=False)  # S3 or local path
    thumbnail_url = Column(String(500))  # For photos/videos
    filename = Column(String(255))
    file_size = Column(Integer)  # Bytes
    mime_type = Column(String(100))

    # Metadata
    caption = Column(Text)
    alt_text = Column(String(255))  # For accessibility

    # AUTOMATIC GEOLOCATION FROM EXIF
    latitude = Column(DECIMAL(10, 7))  # Extracted from GPS EXIF data
    longitude = Column(DECIMAL(10, 7))
    photo_taken_at = Column(TIMESTAMP)  # From EXIF DateTimeOriginal

    # Display settings
    is_hero = Column(Boolean, default=False)  # Hero image for village page
    display_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True, index=True)

    # Audit
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationships
    village = relationship("Village", backref="media")
    uploader = relationship("User", backref="uploaded_media")

    # Valid media types
    VALID_MEDIA_TYPES = ['photo', 'video', 'document']

    # Valid categories
    VALID_CATEGORIES = ['heritage', 'nature', 'community', 'economy', 'events']

    def __repr__(self):
        return f"<VillageMedia(id={self.id}, type='{self.media_type}', filename='{self.filename}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "village_id": self.village_id,
            "media_type": self.media_type,
            "category": self.category,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "filename": self.filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "caption": self.caption,
            "alt_text": self.alt_text,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "photo_taken_at": self.photo_taken_at.isoformat() if self.photo_taken_at else None,
            "is_hero": self.is_hero,
            "display_order": self.display_order,
            "is_published": self.is_published,
            "uploaded_by": self.uploaded_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
