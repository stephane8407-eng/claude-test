"""
User model - Authentication for village admins and system users
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hashed

    # User role and village association
    role = Column(String(20), server_default='user', index=True, nullable=False)
    # Legacy role column - kept for backward compatibility
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True, index=True)
    # New role_id for RBAC system
    village_id = Column(Integer, ForeignKey('villages.id'), nullable=True, index=True)
    # village_id is NULL for system admins, set for village admins

    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))

    # Account status
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP)

    # Relationships
    village = relationship("Village", backref="users")
    role_obj = relationship("Role", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "village_id": self.village_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }

        # Include village slug if user has a village
        if self.village:
            data["village_slug"] = self.village.slug
            data["village_name"] = self.village.name

        # Never include password_hash in API responses unless explicitly needed
        if include_sensitive:
            data["password_hash"] = self.password_hash

        return data
