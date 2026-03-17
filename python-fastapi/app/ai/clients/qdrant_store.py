from qdrant_client import QdrantClient
from app.ai.config import settings
from functools import lru_cache
from langchain_qdrant import QdrantVectorStore
from app.ai.clients.embeddings import get_embeddings
from qdrant_client.models import VectorParams, Distance


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )


@lru_cache(maxsize=1)
def get_vector_store() -> QdrantVectorStore:
    embedding = get_embeddings()
    client = get_qdrant_client()
    dim = len(embedding.embed_query("ping"))

    if not client.collection_exists(settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
    return QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION,
        embedding=embedding,
    )
