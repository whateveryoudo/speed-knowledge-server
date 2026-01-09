from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, func, UniqueConstraint
import uuid
from app.db.base import Base
from typing import Optional
from sqlalchemy.orm import relationship
from app.common.enums import CollectResourceType
class Collect(Base):
    """资源收藏(知识库/文档)"""
    __tablename__ = "collect"
    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", "document_id", name="uix_user_knowledge_document"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False, comment="用户ID")
    resource_type: CollectResourceType = Column(String(20), nullable=False, comment="资源类型")
    knowledge_id: Optional[str] = Column(String(36), ForeignKey("knowledge_base.id", ondelete="CASCADE"), index=True, comment="知识库ID")
    document_id: Optional[str] = Column(String(36), ForeignKey("document_base.id", ondelete="CASCADE"), index=True, comment="文档ID")
    created_at: datetime = Column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
    updated_at: datetime = Column(DateTime, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp(), comment="更新时间")

    user = relationship("User", back_populates="collects")
    knowledge = relationship("Knowledge", back_populates="collects")
    document = relationship("Document", back_populates="collects")
