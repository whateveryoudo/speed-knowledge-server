from typing import Iterator, Dict, Any
from app.ai.robot.speed_doc_robot import get_speed_doc_bot


class RobotAgentAdapter:
    def stream_events(self, content: str, session_id: str) -> Iterator[Dict[str, Any]]:
        agent = get_speed_doc_bot()
        config = {"configurable": {"thread_id": session_id}}
        for event in agent.stream(
            {"messages": [{"role": "user", "content": content}]},
            stream_mode="values",
            config=config,
        ):
            yield event
