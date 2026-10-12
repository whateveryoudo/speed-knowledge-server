"""文档模型"""

from typing import Optional
from app.db.base import Base
from sqlalchemy import (
    UniqueConstraint,
    String,
    Integer,
    ForeignKey,
    func,
    DateTime,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.mysql import LONGTEXT, LONGBLOB
from datetime import datetime
import uuid
from app.common.enums import DocumentType, DocumentVisibility
from app.core.mixins import SoftDeleteMixin


class Document(SoftDeleteMixin, Base):
    """文档模型"""

    __tablename__ = "document_base"

    __table_args__ = (
        UniqueConstraint(
            "knowledge_id", "slug", name="uniq_knowledge_id_document_slug"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属用户",
    )
    knowledge_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属知识库",
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="文档名称")
    slug: Mapped[str] = mapped_column(String(64), nullable=False, comment="文档短链")
    type: Mapped[DocumentType] = mapped_column(
        String(10), nullable=False, comment="文档类型"
    )
    view_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="浏览次数"
    )
    visibility: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=DocumentVisibility.INHERIT.value,
        server_default=DocumentVisibility.INHERIT.value,
        comment="文档可见类别: inherit(继承知识库权限), space(空间内部成员可见),private(不继承知识库的空间/公开范围), public(互联网公开)",
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

    knowledge = relationship("Knowledge", back_populates="documents")
    user = relationship("User", back_populates="documents")
    content = relationship(
        "DocumentContent", back_populates="document", cascade="all, delete"
    )
    nodes = relationship(
        "DocumentNode", back_populates="document", cascade="all, delete"
    )
    collaborators = relationship(
        "Collaborator", back_populates="document", cascade="all, delete"
    )


class DocumentContent(Base):
    """文档内容模型"""

    __tablename__ = "document_content"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属文档",
    )
    node_json: Mapped[str] = mapped_column(
        LONGTEXT, nullable=False, comment="文档内容(为协同编辑的的二进制json数据)"
    )
    content: Mapped[bytes] = mapped_column(
        LONGBLOB, nullable=False, comment="文档内容(为协同编辑的的二进制数据)"
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

    document = relationship("Document", back_populates="content", cascade="all, delete")
