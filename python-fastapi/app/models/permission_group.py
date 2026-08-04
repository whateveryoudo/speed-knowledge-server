from sqlalchemy import Column, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.common.enums import ResourceRole, ResourceType
from uuid import uuid4


class PermissionGroup(Base):
    """权限组模型(用于关联角色和能力)"""

    __tablename__ = "permission_groups"
    __table_args__ = (
        UniqueConstraint(
            "resource_role",
            "target_type",
            "target_id",
            name="uix_resource_role_target_type_target_id",
        ),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False, comment="权限组名称")
    resource_role = Column[ResourceRole](String(30), nullable=False, comment="资源角色")
    target_type = Column[ResourceType](
        String(30), nullable=False, comment="目标类型(knowledge/document)"
    )
    target_id = Column[str](String(36), nullable=False, comment="目标ID(知识库/文档ID)")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    abilities = relationship("PermissionAbility", back_populates="permission_group")
