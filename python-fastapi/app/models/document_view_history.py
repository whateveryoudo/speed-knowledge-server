"""文档浏览历史模型"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from uuid import uuid4
from datetime import datetime


class DocumentViewHistory(Base):
    """文档浏览历史表"""

    __tablename__ = "document_view_history"

    __table_args__ = (
        UniqueConstraint(
            "document_id", "viewed_user_id", name="uniq_document_id_viewed_user_id"
        ),
        # Index('idx_document_id', 'document_id'),
        # Index('idx_viewed_user_id', 'viewed_user_id'),
    )

    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid4()))
    document_id = Column[str](
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属文档",
    )
    viewed_user_id = Column[int](
        Integer, ForeignKey("user.id"), index=True, nullable=False, comment="浏览的用户"
    )
    viewed_datetime = Column[datetime](DateTime, nullable=True, comment="浏览时间")
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

    document = relationship("Document")
    user = relationship("User")
