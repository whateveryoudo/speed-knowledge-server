from functools import lru_cache
from langchain.agents import create_agent
from app.ai.clients.llm import get_llm
from app.ai.tools.doc_tools import get_doc_search_tool
from app.ai.tools.web_tools import web_search

SYSTEM_PROMPT = """你是一个帮助用户解答问题的智能助手。
【非常重要】文档相关问题，需要在已有的知识库中搜寻答案
规则：
1. 除了“实时信息”（天气/新闻/汇率/股票等）外：
   只要用户的问题是“如何/步骤/操作/插入/配置/使用/指南/文档相关”，必须先调用 doc_search。
2. doc_search 的返回结果必须作为回答依据：
   - 不能用常识替代文档里的操作步骤。
   - 如果 doc_search 返回为空，才允许使用 web_search 或通用知识，但必须明确说明“未在知识库找到，只能提供通用建议”。
3. 回答时尽量引用 doc_search 中检索到的原句/要点（必要时做整理），不要编造文档内容。"""


@lru_cache(maxsize=1)
def get_speed_doc_bot():

    llm = get_llm()
    doc_tool = get_doc_search_tool()

    return create_agent(
        model=llm, tools=[doc_tool, web_search], system_prompt=SYSTEM_PROMPT
    )
