from typing import Union
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
    Boolean,
    text,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.common.enums import KnowledgeAbility, DocumentAbility
from uuid import uuid4


class PermissionAbility(Base):
    """权限能力模型(用于关联权限组和能力)"""

    __tablename__ = "permission_abilities"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    permission_group_id = Column(
        String(36),
        ForeignKey("permission_groups.id", ondelete="CASCADE"),
        nullable=False,
        comment="权限组ID",
    )
    ability_key = Column[Union[KnowledgeAbility, DocumentAbility]](
        String(30), nullable=False, comment="能力键"
    )
    enable = Column(
        Boolean, nullable=False, server_default=text("0"), comment="是否启用"
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    permission_group = relationship("PermissionGroup", back_populates="abilities", cascade="all, delete")
