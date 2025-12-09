"""
SponsorSlot model - Links sponsors to objects with analytics
"""
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SponsorSlot(Base):
    __tablename__ = "sponsor_slots"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey('sponsors.id', ondelete='CASCADE'), nullable=False, index=True)
    object_type = Column(String(50), nullable=False, index=True)  # 'settlement', 'route', 'topic'
    object_id = Column(Integer, nullable=False, index=True)
    position = Column(String(20), default='primary')  # 'primary', 'secondary'
    start_date = Column(Date)
    end_date = Column(Date)
    impression_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    sponsor = relationship("Sponsor", back_populates="slots")

    def __repr__(self):
        return f"<SponsorSlot(id={self.id}, sponsor_id={self.sponsor_id}, object_type='{self.object_type}', object_id={self.object_id})>"

    def to_dict(self, include_sponsor=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "sponsor_id": self.sponsor_id,
            "object_type": self.object_type,
            "object_id": self.object_id,
            "position": self.position,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "impression_count": self.impression_count,
            "click_count": self.click_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sponsor and self.sponsor:
            data["sponsor"] = self.sponsor.to_dict()

        return data

    def increment_impressions(self):
        """Increment impression count."""
        self.impression_count = (self.impression_count or 0) + 1

    def increment_clicks(self):
        """Increment click count."""
        self.click_count = (self.click_count or 0) + 1
