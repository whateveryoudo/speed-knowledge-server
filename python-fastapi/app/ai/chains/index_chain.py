from app.ai.tools.get_tiptap_text import get_tiptap_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ai.config import settings
from app.ai.clients.qdrant_store import get_vector_store, get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
from uuid import uuid5

def index_document_form_json(
    *,
    event_id: str,
    knowledge_id: str,
    node_json: str,
    document_id: str,
    content_updated_at: str,
):
    """索引文档"""
    text = get_tiptap_text(node_json)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP
    )
    vector_store = get_vector_store()
    qdrant_client = get_qdrant_client()

    qdrant_client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            ]
        ),
    )
    chunks = splitter.split_text(text)
    metadatas = [
        {
            "knowledge_id": knowledge_id,
            "document_id": document_id,
            "chunk_index": idx,
            "content_updated_at": content_updated_at,
        }
        for idx, chunk in enumerate(chunks)
    ]
    # 这里不存入ids
    # ids = [str(uuid5(document_id.encode(), idx)) for idx in range(len(chunks))]
    vector_store.add_texts(texts=chunks, metadatas=metadatas)
