"""文档节点树"""

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import DocumentNodeType


class DocumentNode(Base):
    """文档节点树"""

    __tablename__ = "document_node"

    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    type = Column[DocumentNodeType](String(10), nullable=False, comment="节点类型")
    title = Column[str](String(128), nullable=False, comment="节点标题")
    parent_id = Column[str](
        String(36),
        ForeignKey("document_node.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="父节点ID",
    )
    first_child_id = Column[str](
        String(36),
        ForeignKey("document_node.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="第一个子节点ID",
    )
    document_id = Column[str](
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属文档ID",
    )
    prev_id = Column[str](
        String(36),
        ForeignKey("document_node.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="前一个节点ID",
    )
    next_id = Column[str](
        String(36),
        ForeignKey("document_node.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="下一个节点ID",
    )
    knowledge_id = Column[str](
        String(36),
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属知识库ID",
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
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )

    document = relationship("Document", backref="nodes")
    @hybrid_property
    def document_slug(self):
        return self.document.slug if self.document else None
