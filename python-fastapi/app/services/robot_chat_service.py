from typing import Iterator, Dict, Any
from app.ai.robot.robot_agent_adapter import RobotAgentAdapter


class RobotChatService:
    def __init__(self, session_id: str):
        self.adapter = RobotAgentAdapter()

    def stream_events(self, content: str, session_id: str) -> Iterator[Dict[str, Any]]:
        last_send = ""
        for event in self.adapter.stream_events(
            content,
            session_id,
        ):
            messages = event.get("messages", [])
            if not messages:
                continue
            last = messages[-1]
            msg_type = getattr(last, "type", None)
            text = getattr(last, "content", None)
            if not text or msg_type != "ai":
                continue
            if text.startswith(last_send):
                delta = text[len(last_send) :]
            else:
                delta = text
            last_send = text
            yield {"content": delta}
        yield {"done": True}
