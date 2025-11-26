"""
UsageEvent model - Simple analytics/event logging for MVP
"""
from sqlalchemy import Column, BigInteger, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(BigInteger, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # page_view, map_click, etc.

    # References (nullable - not every event has all)
    place_id = Column(Integer, ForeignKey('places.id', ondelete='SET NULL'), index=True)
    battle_id = Column(Integer, ForeignKey('battles.id', ondelete='SET NULL'), index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    # Session tracking
    session_id = Column(String(100), index=True)  # Browser session ID
    ip_address_hash = Column(String(64))  # SHA256 hashed for GDPR privacy
    user_agent = Column(Text)  # Browser info
    referrer = Column(String(500))  # Where did they come from?

    # Flexible data
    event_metadata = Column(JSONB)  # Any additional event-specific data

    timestamp = Column(TIMESTAMP, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<UsageEvent(id={self.id}, type='{self.event_type}', timestamp={self.timestamp})>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "place_id": self.place_id,
            "battle_id": self.battle_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address_hash": self.ip_address_hash,
            "user_agent": self.user_agent,
            "referrer": self.referrer,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
