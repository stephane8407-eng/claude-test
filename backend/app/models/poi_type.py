from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database import Base

class POIType(Base):
    __tablename__ = "poi_types"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    name = Column(String(100), nullable=False, unique=True)
    name_plural = Column(String(100))
    category = Column(String(50), nullable=False, index=True)

    # Display settings
    icon = Column(String(50))
    color = Column(String(7), default='#3B82F6')

    # Metadata
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    # pois = relationship("POI", back_populates="poi_type")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'name_plural': self.name_plural,
            'category': self.category,
            'icon': self.icon,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<POIType(id={self.id}, name='{self.name}', category='{self.category}')>"
