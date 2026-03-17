import json
from typing import List, Any

_BLOCK_TYPES = ["paragraph", "heading", "list_item", "code_block", "bullet_list", "ordered_list"]

def _walk(node: Any, result: List[str]) -> None:
    """遍历tiptap节点"""
    if isinstance(node, dict):
        t = node.get("type")
        if t == 'text':
            result.append(node.get("text", ""))
        elif t in _BLOCK_TYPES:
            result.append("\n")
            for child in node.get("content", []):
                _walk(child, result)
            result.append("\n")
    elif isinstance(node, list):
        for child in node:
            _walk(child, result)

def get_tiptap_text(node_json_str: str) -> str:
    """获取tiptap文本"""
    if not node_json_str:
        return ""
    try:
        node_json = json.loads(node_json_str)
        result: List[str] = []
        _walk(node_json, result)
        text = "".join(result)

        lines = [line.strip() for line in text.splitlines()]
        cleaned = []
        prev_empty = False
        for ln in lines:
            is_empty = ln == ""
            if is_empty and prev_empty:
                continue
            cleaned.append(ln)
            prev_empty = is_empty
        return "\n".join(cleaned)
    except Exception as e:
        return ""
