import json
import uuid
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
from app.schemas.ai import Suggestion
from dotenv import load_dotenv

load_dotenv()


chat = ChatTongyi(model_name="qwen-max")



def flatten_tiptap_doc(doc: Dict[str, Any]) -> str:
    """扁平化 tiptap 文档结构

    Args:
        doc (Dict[str, Any]): tiptap 文档结构(json)

    Returns:
        str: 扁平化后的文档内容(包含 title, content, headings, paragraphs, lists, tables, images, etc.)
    """
    result = []

    def walk(node: Dict[str, Any], path: List[int]):
        node_type = node.get("type")
        content = node.get("content", "")

        if node_type == "paragraph":
            text_parts = []
            for c in content:
                if c.get("type") == "text":
                    text_parts.append(c.get("text", ""))
            text = "".join(text_parts).strip()
            if text:
                result.append(f"段落{len(result) + 1}: {text}")
        for child in content:
            if isinstance(child, dict):
                walk(child, path + [0])

    walk(doc, [])
    return "\n".join(result)


def build_prompt(flat_text: str, rules: List[Dict[str, Any]]) -> str:
    result_str = json.dumps(rules, ensure_ascii=False, indent=2)
    return f"""
你是一个政府公文/统计报告规范审稿助手，需要根据“规则”和“全文内容”给出结构化修改建议。
【规则（JSON）】:
{result_str}

【全文内容】:
{flat_text}

请根据规则找出需要修改或补充的地方，输出一个 JSON 数组，数组每个元素形如：
{{
    "id": "string, 唯一标识",
    "from": int, 修改开始位置, // 建议的起始字符索引，基于上面【全文内容】的字符串
    "to": int, 修改结束位置, // 建议的结束字符索引（不含）
    "message": string, 问题说明,
    "rule_id": string, 规则ID,
    "severity": "error/warning/info", 修改级别,
    "replacement": string, 替换内容
    "meta": {{"section": "可选的短链/章节说明"}}
}}

只输出 JSON 数组，不要输出任何其他内容。
""".strip()


def call_llm_for_suggestions(
    doc: Dict[str, Any], rules: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    flat_text = flatten_tiptap_doc(doc)
    prompt = build_prompt(flat_text, rules)
    messages = [HumanMessage(content=prompt)]
    response = chat.invoke(messages)
    try:
        raw_list = json.loads(response.content)
        if not isinstance(raw_list, list):
            return []
    except json.JSONDecodeError:
        return []
    suggestions = []
    for item in raw_list:
        try:
            suggestion = Suggestion(
                id=str(uuid.uuid4()),
                from_=item.get("from", 0),
                to=item.get("to"),
                message=item.get("message"),
                rule_id=item.get("rule_id"),
                severity=item.get("severity"),
                replacement=item.get("replacement"),
                meta=item.get("meta", {}),
            )
            suggestions.append(suggestion)
        except Exception as e:
            print(f"Error parsing suggestion: {e}")
            continue
    return suggestions
