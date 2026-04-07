from typing import Iterator, Dict, Any
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from sqlalchemy.orm import Session


class RobotAgentAdapter:
    def __init__(self, services: dict[str, Any]) -> None:
        self.services = services

    def stream_events(self, content: str, session_id: str) -> Iterator[Dict[str, Any]]:
        agent = get_speed_doc_bot()
        # 注入服务到配置中
        config = {"configurable": {"thread_id": session_id, "services": self.services}}
        for event in agent.stream(
            {"messages": [{"role": "user", "content": content}], "citations": []},
            stream_mode="messages",
            config=config,
        ):
            yield event

        snapshot = agent.get_state(config)
        values = getattr(snapshot, "values", {}) or {}
        yield {"event": "citations", "data": values.get("citations", [])}

