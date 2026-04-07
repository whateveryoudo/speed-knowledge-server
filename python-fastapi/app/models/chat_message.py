from enum import unique
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer, UniqueConstraint    
from app.db.base import Base
import uuid
from datetime import datetime
from app.common.enums import ChatMessageRole, ChatMessageType


class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = (
        UniqueConstraint('answer_group_id', 'id', 'version', name='uniq_answer_group_id_id_version'),
    )

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
    context_json = Column(JSON, nullable=True, comment="上下文json(用于缓存一些替换的上下文)")
    role = Column[ChatMessageRole](String(20), nullable=False, comment="消息角色")
    type = Column[ChatMessageType](String(20), nullable=False, comment="消息类型")
    link_question = Column(String(255), nullable=True, comment="关联问题(用于重新生成答案)")
   
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    answer_group_id = Column(String(36), nullable=False, comment="答案组id")
    version = Column(Integer, nullable=False, default=1, comment="版本")