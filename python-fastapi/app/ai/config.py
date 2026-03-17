from pydantic_settings import BaseSettings
from typing import List


class AIConfig(BaseSettings):
    """ai相关配置"""

    PUBLIC_HELP_KNOWLEDGE_SLUG: str

    QDRANT_URL: str
    QDRANT_COLLECTION: str

    # 本地向量库
    EMBED_MODEL_NAME: str
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    TOP_K: int

    # 千问llmkey
    DASHSCOPE_API_KEY: str
    QWEN_MODEL: str

    # 直接读取环境变量
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AIConfig()
