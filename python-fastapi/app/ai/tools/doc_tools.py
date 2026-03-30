from __future__ import annotations
from re import search
from langchain_core.tools import create_retriever_tool
from langchain.tools import tool
from app.ai.config import settings
from app.ai.retrieval.public_retriever import get_public_retriever
from langchain_core.runnables import RunnableConfig
from app.ai.retrieval.public_retriever import search_public
from app.ai.citation.context import append_citation, next_ref_index


@tool
def doc_search(query: str, config: RunnableConfig) -> str:
    """用于检索企业知识库文档。
    当用户问题与“如何/步骤/操作/插入/配置/使用/指南/文档”相关时，必须调用本工具。
    工具输入参数 query=用户问题；输出是最相关文档片段（拼接后的内容）。
    必须优先基于检索片段回答并引用要点；若检索为空，才允许使用通用知识/或其它搜索。
    """

    docs = search_public(settings.SYNC_VECTOR_KNOWLEDGE_ID, query)
    seen: set[str] = set()
    lines: list[str] = []
    # 获取文档服务
    document_service = (
        config.get("configurable", {}).get("services", {}).get("document_service")
        or None
    )
    if not docs:
        return "未在知识库找到相关文档。"
    doc_rel_link_dict: dict[str, str] = {}
    print("document_service", document_service)
    if document_service:
        # 调用文档服务获取文档相关链接
        document_ids = [doc.get("metadata", {}).get("document_id") for doc in docs]
        doc_rel_link_dict = document_service.resolve_document_links_batch(document_ids)
    ref = next_ref_index()
    for doc in docs:
        meta = doc.get("metadata") or {}
        document_id = meta.get("document_id")
        if not document_id:
            continue
        key = f"doc_{document_id}"
        if key in seen:
            continue
        seen.add(key)

        append_citation(
            {
                "ref": ref,
                # 提取文档相关链接
                "document_link": doc_rel_link_dict.get(document_id, ""),
            }
        )
        body = doc.get("text") or "".strip()
        lines.append(f"【{ref}】\n" f"片段:\n{body}\n")
        ref += 1
    if not lines:
        return "未在知识库找到相关文档。"

    header = (
        "以下为检索到的资料，请仅基于这些内容回答（编号代表链接说明,可选择性带出）；引用处使用 【1】、【2】 等形式，"
        "编号与下方【编号】一致。不要自行编写 http 链接或文档 id。\n\n"
    )
    print(header + "\n---\n".join(lines))
    return header + "\n---\n".join(lines)
