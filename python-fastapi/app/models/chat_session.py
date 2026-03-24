from sqlalchemy import Column, String, DateTime
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums.chat import ChatSessionStatus


class ChatSession(Base):
    __tablename__ = "chat_session"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="会话id",
    )
    user_id = Column(String(36), index=True, comment="用户id")
    title = Column(String(255), nullable=False, comment="会话标题")
    status = Column[ChatSessionStatus](
        String(20), nullable=False, default=ChatSessionStatus.ACTIVE, comment="会话状态"
    )
    last_message_preview = Column(
        String(100), comment="最后一条消息预览(通常用来做摘要)"
    )
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
