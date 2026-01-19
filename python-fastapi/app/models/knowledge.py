"""知识库模型"""

from sqlalchemy import (
    Column,
    BigInteger,
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
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid
from app.schemas.attachment import default_attachment_item
from app.common.enums import KnowledgeIndexPageSort, KnowledgeIndexPageLayout
from app.core.mixins import SoftDeleteMixin
class Knowledge(SoftDeleteMixin, Base):
    """知识库表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "knowledge_base"

    __table_args__ = (
        UniqueConstraint("slug", name="uniq_knowledge_slug"),
    )

    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    user_id = Column[int](Integer, index=True, nullable=False, comment="所属用户")
    group_id = Column[str](
        String(36),
        ForeignKey("knowledge_group.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属分组",
    )
    icon = Column[str](String(20), nullable=False, comment="知识库图标")
    name = Column[str](String(128), nullable=False, comment="知识库名称")
    slug = Column[str](String(64), index=True, nullable=False, unique=True, comment="知识库短链")
    description = Column[str](String(512), nullable=True, comment="简介")
    cover_url = Column(
        JSON,
        default=default_attachment_item.model_dump(),
        nullable=True,
        comment="封面图信息",
    )
    is_public = Column[bool](
        Boolean, nullable=False, server_default=text("0"), comment="是否公开"
    )

    enable_catalog = Column[bool](
        Boolean, nullable=False, server_default=text("1"), comment="是否启用目录"
    )

    enable_custom_body = Column[bool](
        Boolean, nullable=False, server_default=text("0"), comment="是否启用自定义模块"
    )

    enable_user_feed = Column[bool](
        Boolean, nullable=False, server_default=text("0"), comment="是否显示协同人员"
    )
    layout = Column[KnowledgeIndexPageLayout](String(20), default=KnowledgeIndexPageLayout.CATALOG, nullable=False, comment="布局")
    sort = Column[KnowledgeIndexPageSort](String(20), default=KnowledgeIndexPageSort.CATALOG, nullable=False, comment="排序")
    
    team_id = Column[str](String(36), ForeignKey("team.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属团队")
    space_id = Column[str](String(36), ForeignKey("space.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属空间（冗余字段）")
    content_updated_at = Column[datetime](
        DateTime, nullable=True, comment="内容最近更新时间"
    )
    created_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),  # 或 mysql_on_update=func.current_timestamp()
        comment="更新时间",
    )

    team = relationship("Team", back_populates="knowledge_items")
    documents = relationship("Document", back_populates="knowledge", cascade="all, delete")
    group = relationship("KnowledgeGroup", back_populates="knowledge_items")
    collects = relationship("Collect", back_populates="knowledge", cascade="all, delete")
    collaborators = relationship("KnowledgeCollaborator", back_populates="knowledge", cascade="all, delete")