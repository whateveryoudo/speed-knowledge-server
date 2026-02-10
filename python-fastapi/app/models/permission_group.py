

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.common.enums import CollaboratorRole, CollaborateResourceType
from uuid import uuid4

class PermissionGroup(Base):
    """权限组模型(用于关联角色和能力)"""
    __tablename__ = "permission_groups"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False, comment="权限组名称")
    collaborator_id = Column[str](String(36), ForeignKey("collaborator.id", ondelete="CASCADE"), nullable=False, comment="协作记录ID")
    role = Column[CollaboratorRole](Integer, nullable=False, comment="角色")
    target_type = Column[CollaborateResourceType](String(30), nullable=False, comment="目标类型(knowledge/document)")
    target_id = Column[str](String(36), nullable=False, comment="目标ID(知识库/文档ID)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    abilities = relationship("PermissionAbility", back_populates="permission_group")
    collaborator = relationship("Collaborator", back_populates="permission_groups", cascade="all, delete")