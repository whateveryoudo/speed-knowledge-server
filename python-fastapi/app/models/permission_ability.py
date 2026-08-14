from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    func,
    Boolean,
    text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from uuid import uuid4


class PermissionAbility(Base):
    """权限组中的单项能力配置"""

    __tablename__ = "permission_abilities"
    __table_args__ = (
        UniqueConstraint(
            "permission_group_id", "ability_key", name="uq_permission_ability_group_key"
        ),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    permission_group_id = Column(
        String(36),
        ForeignKey("permission_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="权限组ID",
    )
    ability_key = Column(String(50), nullable=False, comment="能力键")
    enabled = Column(
        Boolean, nullable=False, server_default=text("0"), comment="是否启用"
    )
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_onupdate=func.now(), server_default=func.now()
    )

    permission_group = relationship("PermissionGroup", back_populates="abilities")
