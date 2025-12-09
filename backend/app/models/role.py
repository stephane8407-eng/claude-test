"""
Role model - User roles for authorization
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="role_obj")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def has_permission(self, permission_name: str) -> bool:
        """Check if this role has a specific permission"""
        return any(p.name == permission_name for p in self.permissions)
