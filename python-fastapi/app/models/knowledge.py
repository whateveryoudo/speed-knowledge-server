"""知识库模型"""

from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import (
    Boolean,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
    text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.schemas.attachment import default_attachment_item
from app.common.enums import (
    KnowledgeIndexPageSort,
    KnowledgeVisibility,
    KnowledgeIndexPageLayout,
)
from app.core.mixins import SoftDeleteMixin


class Knowledge(SoftDeleteMixin, Base):
    """知识库表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "knowledge_base"

    __table_args__ = (UniqueConstraint("slug", name="uniq_knowledge_slug"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    creator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="知识库创建者",
    )

    space_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("space.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属空间",
    )
    team_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("team.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属团队(允许为空：为空则表示为个人空间或者空间公共区)",
    )
    visibility: Mapped[str] = mapped_column(
        String(20),
        default=KnowledgeVisibility.PRIVATE.value,
        server_default=text("'private'"),
        nullable=False,
        comment="公开范围: private私有, space空间成员可见, public互联网公开",
    )

    icon: Mapped[str] = mapped_column(String(20), nullable=False, comment="知识库图标")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="知识库名称")
    slug: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, unique=True, comment="知识库短链"
    )
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="简介")
    cover_url: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=default_attachment_item.model_dump(),
        nullable=True,
        comment="封面图信息",
    )

    enable_password_protection: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
        comment="是否启用高级密码保护,默认不开启",
    )

    enable_catalog: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("1"), comment="是否启用目录"
    )

    enable_custom_body: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"), comment="是否启用自定义模块"
    )

    enable_user_feed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"), comment="是否显示协同人员"
    )
    layout: Mapped[KnowledgeIndexPageLayout] = mapped_column(
        String(20),
        default=KnowledgeIndexPageLayout.CATALOG,
        nullable=False,
        comment="布局",
    )
    sort: Mapped[KnowledgeIndexPageSort] = mapped_column(
        String(20),
        default=KnowledgeIndexPageSort.CATALOG,
        nullable=False,
        comment="排序",
    )

    content_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="内容最近更新时间"
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
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )

    team = relationship("Team", back_populates="knowledge_items")
    space = relationship("Space", back_populates="knowledge_items")
    creator = relationship("User", foreign_keys=[creator_id])
    grants = relationship(
        "ResourceGrant",
        primaryjoin=(
            "and_(ResourceGrant.resource_type == 'knowledge', foreign(ResourceGrant.resource_id) == Knowledge.id)"
        ),
        viewonly=True,
    )
    documents = relationship(
        "Document", back_populates="knowledge", cascade="all, delete"
    )
    group_relations = relationship(
        "KnowledgeGroupRelation", back_populates="knowledge", cascade="all, delete"
    )
    collaborators = relationship(
        "Collaborator", back_populates="knowledge", cascade="all, delete"
    )
    knowledge_common_pins = relationship(
        "KnowledgeCommonPin", back_populates="knowledge", cascade="all, delete"
    )
