from app.ai.clients.qdrant_store import get_vector_store
from langchain_core.vectorstores import VectorStoreRetriever
from app.ai.config import settings
from typing import List, Dict, Any


def get_public_retriever(knowledge_id: str) -> VectorStoreRetriever:
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_kwargs={
            "k": settings.TOP_K,
            "filter": {"must": [{"key": "metadata.knowledge_id", "match": {"value": knowledge_id}}]},
        }
    )


def search_public(knowledge_id: str, query: str) -> List[Dict[str, Any]]:
    retriever = get_public_retriever(knowledge_id)
    docs = retriever.invoke(query)
    return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]
