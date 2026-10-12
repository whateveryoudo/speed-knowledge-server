from typing import Optional, Any
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import ChatMessageRole, ChatMessageType


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="消息id",
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("chat_session.id"),
        index=True,
        nullable=True,
        comment="会话id",
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    role: Mapped[ChatMessageRole] = mapped_column(
        String(20), nullable=False, comment="消息角色"
    )
    type: Mapped[ChatMessageType] = mapped_column(
        String(20), nullable=False, comment="消息类型"
    )
    link_question: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="关联问题(用于重新生成答案)"
    )
    suggestions: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="建议列表"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, nullable=True, comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=True, comment="更新时间"
    )
