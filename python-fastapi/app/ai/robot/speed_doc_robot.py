from functools import lru_cache
from typing import Annotated, operator, TypedDict
from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from app.ai.clients.llm import get_llm
from app.ai.tools.doc_tools import doc_search
from app.ai.tools.web_tools import web_search
import operator

SYSTEM_PROMPT = """你是一个帮助用户解答问题的智能助手。
【非常重要】文档相关问题，需要在已有的知识库中搜寻答案
规则：
1. 除了“实时信息”（天气/新闻/汇率/股票等）外：
   只要用户的问题是“如何/步骤/操作/插入/配置/使用/指南/文档相关”，必须先调用 doc_search。
2. doc_search 的返回结果必须作为回答依据：
   - 不能用常识替代文档里的操作步骤。
   - 如果 doc_search 返回为空，才允许使用 web_search 或通用知识，但必须明确说明“未在知识库找到，只能提供通用建议”。
3. 回答时尽量引用 doc_search 中检索到的原句/要点（必要时做整理），不要编造文档内容。"""


class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


tools = [doc_search(), web_search]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = get_llm().bind_tools(tools)


def llm_call(state: State) -> State:
    """
    单节点处理大模型决策和工具调用
    """
    response = model_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )
    return {"messages": [response]}


def tool_node(state: State) -> State:
    """
    工具调用节点
    """
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        print(tool_call)
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        results.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": results}


def should_continue(state: State) -> bool:
    """
    判断是否继续执行
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


graph = StateGraph(State)
graph.add_node("llm_call", llm_call)
graph.add_node("tools", tool_node)

graph.add_edge(START, "llm_call")
graph.add_conditional_edges("llm_call", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "llm_call")


@lru_cache(maxsize=1)
def get_speed_doc_bot():
    agent = graph.compile()
    display(Image(agent.get_graph().draw_mermaid_png()))
    return agent
