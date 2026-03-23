from langchain_core.tools import create_retriever_tool
from langchain.tools import tool
from app.ai.config import settings
from app.ai.retrieval.public_retriever import get_public_retriever


def doc_search():
    """获取检索器"""
    retriever = get_public_retriever(settings.SYNC_VECTOR_KNOWLEDGE_ID)
    tool = create_retriever_tool(
        retriever,
        name="doc_search",
        description=(
            "用于检索企业知识库文档。"
            "当用户问题与“如何/步骤/操作/插入/配置/使用/指南/文档”相关时，必须调用本工具。"
            "工具输入参数 query=用户问题；输出是最相关文档片段（拼接后的内容）。"
            "必须优先基于检索片段回答并引用要点；若检索为空，才允许使用通用知识/或其它搜索。"
        ),
    )
    return tool
