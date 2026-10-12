from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, Integer, Enum, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.common.enums import TeamVisibility
from app.core.mixins import SoftDeleteMixin


class Team(SoftDeleteMixin, Base):
    """团队表（承载个人和团队空间）"""

    __tablename__ = "team"

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(30), nullable=False, comment="团队名称")
    icon: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="团队图标(类型或图片url)"
    )
    slug: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        unique=True,
        comment="团队标识(用于访问知识库的时候携带)",
    )
    space_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("space.id", ondelete="CASCADE"),
        nullable=False,
        comment="空间ID",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="团队简介"
    )
    visibility: Mapped[TeamVisibility] = mapped_column(
        Enum(TeamVisibility),
        nullable=False,
        comment="团队可见性(公开给空间所有成员)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="更新时间",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否为默认团队"
    )
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="团队所有者ID",
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="加入时间",
    )

    team_members = relationship(
        "TeamMember", back_populates="team", cascade="all, delete"
    )
    knowledge_items = relationship(
        "Knowledge", back_populates="team", cascade="all, delete"
    )