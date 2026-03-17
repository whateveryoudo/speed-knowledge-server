from app.ai.clients.qdrant_store import get_vector_store
from langchain.retrievers import VectorStoreRetriever
from app.ai.config import settings
from typing import List, Dict, Any


def get_public_retriever(knowledge_slug: str) -> VectorStoreRetriever:
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_kwargs={
            "k": settings.TOP_K,
            "filter": {"knowledge_slug": knowledge_slug},
        }
    )


def search_public(knowledge_slug: str, query: str) -> List[Dict[str, Any]]:
    retriever = get_public_retriever(knowledge_slug)
    docs = retriever.get_relevant_documents(query)
    return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]
