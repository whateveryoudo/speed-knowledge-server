from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from app.ai.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.EMBED_MODEL_NAME,
        model_kwargs={"device": "cpu"},
    )