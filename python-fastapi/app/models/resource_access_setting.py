"""知识库访问的一些配置（存放高级密码保护配置）"""

from typing import Optional
from app.db.base import Base
from sqlalchemy import String, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.common.enums import CollaborateResourceType
import uuid


class ResourceAccessSetting(Base):
    __tablename__ = "resource_access_setting"
    __table_args__ = (
        UniqueConstraint("target_id", "target_type", name="uix_target_id_target_type"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    target_id: Mapped[str] = mapped_column(
        String(36), comment="目标ID", nullable=False
    )
    target_type: Mapped[CollaborateResourceType] = mapped_column(
        String(30), comment="目标类型(knowledge, document)", nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(4), comment="密码(这里为4位字符明文)", nullable=False
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), nullable=True, comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True, comment="更新时间"
    )
