from pydantic_settings import BaseSettings
from typing import List, Optional


class AIConfig(BaseSettings):
    """ai相关配置"""

    SYNC_VECTOR_KNOWLEDGE_ID: str

    QDRANT_URL: str
    QDRANT_COLLECTION: str
    QDRANT_API_KEY: Optional[str]
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
        extra="allow"


settings = AIConfig()
