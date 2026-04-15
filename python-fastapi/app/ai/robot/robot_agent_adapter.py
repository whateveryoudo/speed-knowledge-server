from typing import Iterator, Dict, Any
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from sqlalchemy.orm import Session
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.clients.llm import get_llm
import json

SUGGESTIONS_SYSTEM_PROMPT = "你只允许输出严格 JSON，不要输出其它任何文字。"
SUGGESTIONS_PROMPT_TEMPLATE = """
请基于下面的“用户问题”和“助手回答”，生成 3 条可继续追问的建议。
要求：
- 必须与主题强相关
- 每条 text 不超过 30 字
- 返回严格 JSON：{{"items":[{{"id":"1","text":"..."}},{{"id":"2","text":"..."}},{{"id":"3","text":"..."}}]}}

用户问题：
{question}

助手回答：
{answer}
""".strip()


class RobotAgentAdapter:
    def __init__(self, services: dict[str, Any]) -> None:
        self.services = services

    def stream_events(self, content: str, session_id: str) -> Iterator[Dict[str, Any]]:
        agent = get_speed_doc_bot()
        # 注入服务到配置中
        config = {"configurable": {"thread_id": session_id, "services": self.services}}
        for event in agent.stream(
            {"messages": [{"role": "user", "content": content}]},
            stream_mode="messages",
            config=config,
        ):
            yield event

    def _parse_json(self, raw: str) -> dict:
        raw = (raw or "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start > -1 and end > 1 and end > start:
                raw = raw[start : end + 1]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
            return {}

    def generate_suggestions(self, question: str, answer: str) -> list[dict[str, str]]:
        llm = get_llm()
        prompt = SUGGESTIONS_PROMPT_TEMPLATE.format(question=question, answer=answer)
        response = llm.invoke(
            [SystemMessage(SUGGESTIONS_SYSTEM_PROMPT), HumanMessage(prompt)]
        )
        raw = getattr(response, "content", "") or ""
        data = self._parse_json(raw)
        # 取前3条
        res: list[dict[str, str]] = []
        for index, item in enumerate(data.get("items", [])):
            if index < 3:
                if isinstance(item, dict) and "id" in item and "text" in item:
                    res.append(
                        {
                            "id": item["id"],
                            "text": item["text"],
                        }
                    )
        return res
