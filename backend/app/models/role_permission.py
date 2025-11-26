"""
RolePermission model - Junction table for roles and permissions
"""
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, PrimaryKeyConstraint
from sqlalchemy.sql import func
from app.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
