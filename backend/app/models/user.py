"""
User model - Basic admin authentication for MVP
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hashed
    first_name = Column(String(100))
    last_name = Column(String(100))
    user_role = Column(String(20), server_default='free', index=True)  # admin, free
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.user_role}')>"

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "user_role": self.user_role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Never include password_hash in API responses unless explicitly needed
        if include_sensitive:
            data["password_hash"] = self.password_hash

        return data
