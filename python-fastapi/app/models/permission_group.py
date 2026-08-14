from sqlalchemy import Column, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.common.enums import PermissionScopeType
from uuid import uuid4


class PermissionGroup(Base):
    """某个作用域下，一个角色对应的一组可配置能力"""

    __tablename__ = "permission_groups"
    __table_args__ = (
        UniqueConstraint(
            "role_key",
            "scope_type",
            "scope_id",
            name="uq_permission_group_scope_role",
        ),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False, comment="权限组名称")
    role_key = Column(String(30), nullable=False, comment="资源角色")
    scope_type = Column[PermissionScopeType](
        String(30), nullable=False, comment="作用域类型：knowledge/document/space/team"
    )
    scope_id = Column(String(36), nullable=False, comment="作用域ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_onupdate=func.now(), server_default=func.now()
    )
    abilities = relationship(
        "PermissionAbility",
        back_populates="permission_group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
