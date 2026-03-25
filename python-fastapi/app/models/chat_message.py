from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import ChatMessageRole, ChatMessageType


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(
        String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        comment="消息id",
    )
    session_id = Column(
        String(36), ForeignKey("chat_session.id"), index=True, comment="会话id"
    )
    content = Column(Text, nullable=False, comment="消息内容")
    role = Column[ChatMessageRole](String(20), nullable=False, comment="消息角色")
    type = Column[ChatMessageType](String(20), nullable=False, comment="消息类型")
   
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )
