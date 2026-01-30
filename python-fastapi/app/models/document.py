"""文档模型"""

from app.db.base import Base
from sqlalchemy import Column, UniqueConstraint, String, Text, Integer, ForeignKey, func, DateTime, LargeBinary, Boolean, text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.common.enums import DocumentType
from app.core.mixins import SoftDeleteMixin
class Document(SoftDeleteMixin, Base):
    """文档模型"""

    __tablename__ = "document_base"

    __table_args__ = (
        UniqueConstraint('knowledge_id', 'slug', name='uniq_knowledge_id_document_slug'),
    )


    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True, comment="主键")
    user_id = Column[int](Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属用户")
    knowledge_id = Column[str](String(36), ForeignKey("knowledge_base.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属知识库")
    name = Column[str](String(128), nullable=False, comment="文档名称")
    slug = Column[str](String(64), nullable=False, comment="文档短链")
    type = Column[DocumentType](String(10), nullable=False, comment="文档类型")
    is_public = Column[bool](Boolean, nullable=False, server_default=text("0"), comment="是否公开")
    view_count = Column[int](Integer, nullable=False, default=0, comment="浏览次数")
    content_updated_at = Column[datetime](DateTime, nullable=True, comment="内容最近更新时间")
    created_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp(), comment="更新时间")


    knowledge = relationship("Knowledge", back_populates="documents")
    user = relationship("User", back_populates="documents")
    content = relationship("DocumentContent", back_populates="document", cascade="all, delete")
    nodes = relationship("DocumentNode", back_populates="document", cascade="all, delete")
    collects = relationship("Collect", back_populates="document", cascade="all, delete")
    collaborators = relationship("Collaborator", back_populates="document", cascade="all, delete")
class DocumentContent(Base):
    """文档内容模型"""

    __tablename__ = "document_content"

   
    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True, comment="主键")
    document_id = Column[str](String(36), ForeignKey("document_base.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属文档")
    node_json = Column[str](Text, nullable=False, comment="文档内容(为协同编辑的的二进制json数据)")
    content = Column(LargeBinary, nullable=False, comment="文档内容(为协同编辑的的二进制数据)")
    content_updated_at = Column[datetime](DateTime, nullable=True, comment="内容最近更新时间")
    created_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp(), comment="更新时间")

    document = relationship("Document", back_populates="content", cascade="all, delete")