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
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid
from app.schemas.attachment import default_attachment_item


class Knowledge(Base):
    """知识库表

    Args:
        Base (_type_): 基类
    """

    __tablename__ = "knowledge_base"

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
    slug = Column[str](String(64), nullable=False, comment="知识库短链")
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
    items_count = Column[int](
        Integer, nullable=False, server_default=text("0"), comment="文档数量"
    )
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
    
    group = relationship("KnowledgeGroup", back_populates="knowledge_items")
