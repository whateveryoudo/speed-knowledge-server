from __future__ import annotations
from typing import Iterator, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.ai.robot.robot_agent_adapter import RobotAgentAdapter
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.schemas.chat_message import ChatMessageCreate, ChatMessageUpdate
from app.schemas.chat_session import ChatSessionUpdate
from app.common.enums import ChatMessageRole, ChatMessageType
from app.common.utils import get_field
from app.services.document_service import DocumentService


class RobotChatService:
    def __init__(self, db: Session, session_id: str):
        # 这里注入一些服务
        document_service = DocumentService(db)
        self.adapter = RobotAgentAdapter(
            {
                "document_service": document_service,
            }
        )
        self.chat_session_service = ChatSessionService(db)
        self.chat_message_service = ChatMessageService(db)

    def stream_events(
        self, input: str, session_id: str, message_id: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        if message_id is None or message_id == "":
            # 非重新生成消息，则初始化消息
            self.chat_message_service.create(
                ChatMessageCreate(
                    session_id=session_id,
                    content=input,
                    role=ChatMessageRole.USER,
                    type=ChatMessageType.TEXT,
                )
            )

        full_text_parts: list[str]() = []
        yield {
            "event": "context",
            "data": {"session_id": session_id},
        }
        for chunk, meta in self.adapter.stream_events(
            input,
            session_id,
        ):
            chunk_type = getattr(chunk, "type", "") or chunk.__class__.__name__
            token = getattr(chunk, "content", "") or ""
            if "AIMessageChunk" not in str(chunk_type):
                continue
            if not token:
                continue

            full_text_parts.append(token)
            yield {"event": "message", "data": token}
        full_text = "".join(full_text_parts)
        # 会话的摘要更新
        self.chat_session_service.update(
            session_id, ChatSessionUpdate(last_message_preview=full_text[:50])
        )
        # 增加建议生成
        suggestions = self.adapter.generate_suggestions(input, full_text)
        yield {"event": "suggestions", "data": suggestions}
        # ai消息更新
        if message_id:
            self.chat_message_service.update(
                ChatMessageUpdate(
                    id=message_id,
                    content=full_text,
                    suggestions=suggestions,
                )
            )
        else:
            self.chat_message_service.create(
                ChatMessageCreate(
                    session_id=session_id,
                    content=full_text,
                    role=ChatMessageRole.ASSISTANT,
                    type=ChatMessageType.TEXT,
                    link_question=input,
                    suggestions=suggestions,
                )
            )
        
        yield {"event": "done", "data": "complete"}
