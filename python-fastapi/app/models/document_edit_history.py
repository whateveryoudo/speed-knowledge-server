"""文档编辑历史模型"""

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from uuid import uuid4
from datetime import datetime


class DocumentEditHistory(Base):
    """文档编辑历史表"""

    __tablename__ = "document_edit_history"

    __table_args__ = (
        UniqueConstraint(
            "document_id", "edited_user_id", name="uniq_document_id_edited_user_id"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属文档",
    )
    edited_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        index=True,
        nullable=False,
        comment="编辑的用户",
    )
    edited_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.current_timestamp(),
        comment="编辑时间",
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

    document = relationship("Document")
    user = relationship("User")
