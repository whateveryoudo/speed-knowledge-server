from typing import Optional
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums.chat import ChatSessionStatus
from app.core.mixins import SoftDeleteMixin


class ChatSession(SoftDeleteMixin, Base):
    __tablename__ = "chat_session"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="会话id",
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, index=True, nullable=True, comment="用户id"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="会话标题")
    status: Mapped[ChatSessionStatus] = mapped_column(
        String(20), nullable=False, default=ChatSessionStatus.ACTIVE, comment="会话状态"
    )
    last_message_preview: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="最后一条消息预览(通常用来做摘要)"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, nullable=True, comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=True, comment="更新时间"
    )
