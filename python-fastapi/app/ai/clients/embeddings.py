from functools import lru_cache

# 生产 slim 镜像未安装 langchain-huggingface / torch。
# 本地 AI 调试: uv sync --group ai
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings

from app.ai.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> DashScopeEmbeddings:
    # 切换为 DashScopeEmbeddings（在线，服务器打包太大了）
    return DashScopeEmbeddings(
        model=settings.EMBED_MODEL_NAME,
        dashscope_api_key=settings.DASHSCOPE_API_KEY,
    )
