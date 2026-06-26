from functools import lru_cache

# 生产 slim 镜像未安装 langchain-huggingface / torch。
# 本地 AI 调试: uv sync --group ai
from langchain_huggingface import HuggingFaceEmbeddings

from app.ai.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.EMBED_MODEL_NAME,
        model_kwargs={"device": "cpu"},
    )
