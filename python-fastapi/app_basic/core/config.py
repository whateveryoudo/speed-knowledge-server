"""应用配置"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    # 应用信息
    APP_NAME: str = "FastAPI Server"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # 数据库
    DATABASE_URL: str

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD:str = ""
    REDIS_DECODE_RESPONSES: bool = True

    # 安全 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

