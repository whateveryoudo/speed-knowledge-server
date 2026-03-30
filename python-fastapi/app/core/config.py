from pydantic_settings import BaseSettings
from typing import List


# 结合env配置文件，同名属性会自动从环境变量中获取
class Settings(BaseSettings):
    """应用设置"""

    APP_NAME: str
    API_V1_STR: str
    PORT: int
    DEBUG: bool
    DOMAIN: str

    # CORS配置
    CORS_ORIGINS_RAW: str = "*"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if not self.CORS_ORIGINS_RAW or self.CORS_ORIGINS_RAW == "*":
            return ["*"]
        # 按逗号分割，并去除每个 URL 前后的空格
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",")]

    # Redis配置

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    REDIS_DECODE_RESPONSES: bool

    # 数据库配置
    DATABASE_URL: str
    # MinIO链接配置(注意：这里的endpoint不要携带协议头)
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_USE_SSL: bool
    # jwt
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # nodejs服务地址
    NODEJS_SERVICE_URL: str

    # mq队列

    RABBITMQ_URL: str
    RABBITMQ_ROUTING_KEY: str
    RABBITMQ_EXCHANGE: str

    RABBITMQ_QUEUE: str
    # 重试
    RABBITMQ_RETRY_QUEUE: str
    # 死信
    RABBITMQ_DLQ_QUEUE: str

    # 重试次数和间隔
    RABBITMQ_MAX_RETRIES: int
    RABBITMQ_RETRY_DELAY_MS: int

    # onlyoffice配置
    ONLYOFFICE_JWT_SECRET: str
    ONLYOFFICE_SERVER_URL: str

    # 火山引擎配置
    VOLC_API_KEY: str
    VOLC_ENDPOINT: str
    # sdk自动填入了端点id
    VOLC_MODEL: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
