import json
import uuid
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
from typing import Dict, Any, List
from app.schemas.ai import Suggestion
from dotenv import load_dotenv
import os

load_dotenv()


chat = ChatTongyi(api_key=os.getenv("DASHSCOPE_API_KEY"), model_name="qwen-max", timeout=30)
def build_tools_str(fixable_rules: List[Dict[str, Any]]) -> str:
    """构建工具字符串

    Args:
        rules (Dict[str, Any]): 规则(json)

    Returns:
        str: 构建后的工具字符串
    """
    tools_definition = []
    for rule in fixable_rules:
        tool_desc = f"""
- **Rule ID**: `{rule['id']}`
  - **Description**: {rule['description']}
  - **Action**: `{rule['fixCommand']['action']}`
  - **Params Template**: {json.dumps(rule['fixCommand'].get('params', {}), ensure_ascii=False)}
"""
        tools_definition.append(tool_desc)
    tools_str = (
        "\n".join(tools_definition) if tools_definition else "暂无可自动修复的规则。"
    )
    return tools_str


def build_prompt(doc: Dict[str, Any], rules: List[Dict[str, Any]]) -> str:
    doc_str = json.dumps(doc, ensure_ascii=False, indent=2)
    result_str = json.dumps(rules, ensure_ascii=False, indent=2)
    tools_str = build_tools_str(rules)
    return f"""
你是一个政府公文/统计报告规范审稿助手，精通Tiptap和ProseMirror的文档结构，你可以参考：[https://tiptap.dev/docs/editor/core-concepts/nodes-and-marks]，需要根据“规则”和“全文内容”给出结构化修改建议。
【规则（JSON）】:
{result_str}
文档结构说明：
- 每个块级节点（如 paragraph, heading）都有唯一的 `attrs.nodeId`。
- 块级节点内部包含多个子节点，其中 `type: "text"` 的节点代表文本片段。
- **注意**：text 节点本身没有 ID。
- text包含marks属性，为list, 包含textStyle

# Available Fix Tools (动态生成的可执行命令)
当发现错误且规则定义了 `fixCommand` 时，你必须严格使用该规则定义的 `action` 和 `params` 结构生成修复指令。
以下是每个规则对应的修复工具定义：

{tools_str}

【全文内容】:
{doc_str}

请根据规则找出需要修改或补充的地方，输出一个 JSON 数组，数组每个元素形如：
1. **整段错误**（如段落缩进不对）：只返回 `nodeId`。
2. **局部错误**（如错别字、某段文字颜色不对）：
   - 返回 `node_id` (所在段落)。
   - 返回 `text_index` (整数)：表示错误发生在该段落内的**第几个 text 节点**（从 0 开始计数）。
   - **重要**：遍历时只统计 `type === "text"` 的节点，忽略其他类型。
输出示例：
[
{{
    "id": "string, 唯一标识",
    "node_id": "string, 唯一标识",
    "text_index": int, 文本节点索引,
    "message": string, 问题说明,
    "rule_id": string, 规则ID,
    "severity": "error/warning/info", 修改级别,
    "fixCommand": {{
        "action": "string (必须与规则定义一致)",
        "params": "object (必须与规则定义一致，只获取key值，value要从description中判断如何设置，可替换具体值)"
    }} | null, 
    "meta": {{"section": "可选的短链/章节说明"}}
}}
]
每条建议必须包含合法的 node_id（字符串），否则视为无效建议
只输出 JSON 数组，不要输出任何其他内容。
""".strip()


def call_llm_for_suggestions(
    doc: Dict[str, Any], rules: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    prompt = build_prompt(doc, rules)
    print(prompt);
    messages = [HumanMessage(content=prompt)]
    
    try:
        print(f"Prompt: {prompt}")
        response = chat.invoke(messages)
        raw_list = json.loads(response.content)
        if not isinstance(raw_list, list):
            return []
    except Exception as e:
        print(f"error: {e}")
        return []
    suggestions = []
    for item in raw_list:
        try:
            suggestion = Suggestion(
                id=str(uuid.uuid4()),
                node_id=item.get("node_id"),
                message=item.get("message"),
                text_index=item.get("text_index"),
                rule_id=item.get("rule_id"),
                severity=item.get("severity"),
                fixCommand=item.get("fixCommand"),
                meta=item.get("meta", {}),
            )
            suggestions.append(suggestion)
        except Exception as e:
            print(f"Error parsing suggestion: {e}")
            continue
    return suggestions
