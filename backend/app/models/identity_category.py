from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class IdentityCategory(Base):
    __tablename__ = "identity_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    name_fr = Column(String(50))
    icon = Column(String(50))
    color = Column(String(7))
    description = Column(Text)
    example_themes = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())

    # Relationships
    identity_themes = relationship("IdentityTheme", back_populates="category")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "name_fr": self.name_fr,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "example_themes": self.example_themes
        }
