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
import uuid


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
        self, input: str, session_id: str, answer_group_id: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        if answer_group_id is None or answer_group_id == "":
            # 非重新生成消息，则初始化消息(用户)
            self.chat_message_service.create(
                ChatMessageCreate(
                    session_id=session_id,
                    content=input,
                    role=ChatMessageRole.USER,
                    type=ChatMessageType.TEXT,
                )
            )

        full_text_parts: list[str] = []
        citations: list[dict] = []
        for event in self.adapter.stream_events(
            input,
            session_id,
        ):
            if isinstance(event, tuple):
                chunk, meta = event
                chunk_type = getattr(chunk, "type", "") or chunk.__class__.__name__
                token = getattr(chunk, "content", "") or ""
                if "AIMessageChunk" not in str(chunk_type):
                    continue
                if not token:
                    continue
                full_text_parts.append(token)
                yield {"event": "message", "data": token}
                continue

            if isinstance(event, dict) and event.get("event") == "citations":
                citations = event.get("data") or []
        full_text = "".join(full_text_parts)
        # ai消息更新
        if answer_group_id:
            self.chat_message_service.update(
                ChatMessageUpdate(
                    answer_group_id=answer_group_id,
                    content=full_text,
                    # 存入数据库
                    context_json=citations,
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
                )
            )
        # 会话的摘要更新
        self.chat_session_service.update(
            session_id, ChatSessionUpdate(last_message_preview=full_text[:50])
        )
        yield {
            "event": "context",
            "data": {"session_id": session_id, "citations": citations},
        }
        yield {"event": "done", "data": "complete"}
