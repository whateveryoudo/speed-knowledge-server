from typing import Iterator, Dict, Any
from sqlalchemy.orm import Session
from app.ai.robot.robot_agent_adapter import RobotAgentAdapter
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.schemas.chat_message import ChatMessageCreate
from app.common.enums import ChatMessageRole, ChatMessageType
from app.common.utils import get_field
import json


class RobotChatService:
    def __init__(self, db: Session, session_id: str):
        self.adapter = RobotAgentAdapter()
        self.chat_session_service = ChatSessionService(db)
        self.chat_message_service = ChatMessageService(db)

    def stream_events(self, content: str, session_id: str) -> Iterator[Dict[str, Any]]:
        last_send = ""
        for event in self.adapter.stream_events(
            content,
            session_id,
        ):
            print(event)
            messages = event.get("messages", [])
            if not messages:
                continue
            last = messages[-1]
            msg_type = get_field(last, "type", None)
            if msg_type == "ai":
                # AIMessage
                tool_calls = get_field(last, "additional_kwargs", {}).get("tool_calls")
                if tool_calls is None:
                    self.chat_message_service.create(
                        ChatMessageCreate(
                            session_id=session_id,
                            content=json.dumps(
                                tool_calls,
                                ensure_ascii=False,
                            ),
                            role=ChatMessageRole.ASSISTANT,
                            type=ChatMessageType.TOOL_CALL,
                        )
                    )
                else:
                    self.chat_message_service.create(
                        ChatMessageCreate(
                            session_id=session_id,
                            content=get_field(last, "content"),
                            role=ChatMessageRole.ASSISTANT,
                            type=ChatMessageType.TEXT,
                        )
                    )

            elif msg_type == "tool":
                # ToolMessage
                self.chat_message_service.create(
                    ChatMessageCreate(
                        session_id=session_id,
                        content=json.dumps(
                            {
                                "content": get_field(last, "content"),
                                "tool_call_id": get_field(last, "tool_call_id"),
                            },
                            ensure_ascii=False,
                        ),
                        role=ChatMessageRole.TOOL,
                        type=ChatMessageType.TOOL_RESULT,
                    )
                )
            else:
                if get_field(last, "role", None) == "user":
                    # 人类输入
                    self.chat_message_service.create(
                        ChatMessageCreate(
                            session_id=session_id,
                            content=get_field(last, "content"),
                            role=ChatMessageRole.USER,
                            type=ChatMessageType.TEXT,
                        )
                    )
            text = get_field(last, "content", None)

            if not text or msg_type != "ai":
                continue
            if text.startswith(last_send):
                delta = text[len(last_send) :]
            else:
                delta = text
            last_send = text
            yield {"content": delta}
        yield {"done": True}
