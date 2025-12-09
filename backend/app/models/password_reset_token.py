"""
PasswordResetToken model - Short-lived tokens for password reset flow
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Token details
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    # We store the hash, not the actual token (sent only via email)

    # Status
    used = Column(Boolean, default=False, nullable=False, index=True)
    expires_at = Column(TIMESTAMP, nullable=False, index=True)
    # Typically 1 hour expiry

    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    used_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "used": self.used,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "used_at": self.used_at.isoformat() if self.used_at else None,
        }
