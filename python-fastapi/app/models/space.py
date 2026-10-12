from app.core.mixins import SoftDeleteMixin
import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, JSON, func, ForeignKey, Integer
from app.db.base import Base
from app.common.enums import SpaceType
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Space(SoftDeleteMixin, Base):
    __tablename__ = "space"

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    type: Mapped[str] = mapped_column(
        String(20), default=SpaceType.PERSONAL.value, nullable=False, comment="空间类型"
    )
    domain: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
        comment="空间域名,也用于标识访问(可选,个人类型可不传入domain)",
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="空间名称")
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="空间所有者ID",
    )
    contact_email: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="联系邮箱,用于接收通知"
    )
    icon: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="封面图信息",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="空间描述"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    public_area_slug: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True, comment="公共区域短链"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="更新时间",
    )

    space_members = relationship(
        "SpaceMember", back_populates="space", cascade="all, delete"
    )
    knowledge_items = relationship("Knowledge", back_populates="space")