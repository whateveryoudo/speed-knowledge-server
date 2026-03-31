from __future__ import annotations
from typing import Iterator, Dict, Any
from sqlalchemy.orm import Session
from app.ai.robot.robot_agent_adapter import RobotAgentAdapter
from app.ai.citation.context import get_citations
from app.ai.citation.replace import replace_citation_brackets
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.schemas.chat_message import ChatMessageCreate
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

    def stream_events(self, input: str, session_id: str) -> Iterator[Dict[str, Any]]:
        self.chat_message_service.create(
            ChatMessageCreate(
                session_id=session_id,
                content=input,
                role=ChatMessageRole.USER,
                type=ChatMessageType.TEXT,
            )
        )

        full_text_parts: list[str]() = []
        # 提供给前端会话id,本次会话设计到的链接映射（这里都放到context类型中）
        citations = get_citations()
        yield {
            "event": "context",
            "data": {"session_id": session_id, "citations": citations},
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
        # ai消息更新
        self.chat_message_service.create(
            ChatMessageCreate(
                session_id=session_id,
                content=replace_citation_brackets(full_text),
                role=ChatMessageRole.ASSISTANT,
                type=ChatMessageType.TEXT,
            )
        )
        # 会话的摘要更新
        self.chat_session_service.update(
            session_id, ChatSessionUpdate(last_message_preview=full_text[:50])
        )
        yield {"event": "done", "data": "complete"}
