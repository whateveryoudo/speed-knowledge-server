"""知识库分组模型"""

from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import (
    Integer,
    String,
    JSON,
    text,
    Boolean,
    func,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.schemas.knowledge_group import DEFAULT_DISPLAY_CONFIG


class KnowledgeGroup(Base):
    """知识库分组模型(调整为多模态模式)"""

    __tablename__ = "knowledge_group"

    __table_args__ = (
        Index("ix_knowledge_group_scope", "scope_type", "scope_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="分组ID",
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        index=True,
        nullable=True,
        comment="创建者id",
    )
    scope_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    scope_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    group_name: Mapped[Optional[str]] = mapped_column(
        String(255), default="新建分组", index=True, nullable=True, comment="分组名称"
    )
    order_index: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0"), nullable=True, comment="排序索引"
    )
    is_default: Mapped[Optional[bool]] = mapped_column(
        Boolean, default=False, nullable=True, comment="是否默认分组"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=True, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=True,
        comment="更新时间",
    )

    display_config: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=DEFAULT_DISPLAY_CONFIG.model_dump(),
        nullable=True,
        comment="显示配置",
    )
    group_relations = relationship(
        "KnowledgeGroupRelation", back_populates="group", cascade="all, delete"
    )
    creator = relationship(
        "User",
        primaryjoin="KnowledgeGroup.created_by == foreign(User.id)",
        uselist=False,
    )
