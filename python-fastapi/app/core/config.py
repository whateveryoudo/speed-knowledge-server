from pydantic_settings import BaseSettings

# TODO： 结合env配置文件
class Settings(BaseSettings):
    """应用设置"""

    APP_NAME: str = "FastAPI Server"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8010
    DEBUG: bool = True

    # Redis配置

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_DECODE_RESPONSES: bool = True

    # 数据库配置
    DATABASE_URL:str = "mysql+pymysql://root:onemoretime123.@localhost:3306/speed-knowledge"
    # MinIO链接配置(注意：这里的endpoint不要携带协议头)
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "speed-knowledge"
    MINIO_USE_SSL:bool = False
    # jwt 
    SECRET_KEY:str='fa44273b1571628e36b527acabe1c06d796fad30cbb4ac40c93fdb10a30bb90f'
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # nodejs服务地址
    NODEJS_SERVICE_URL: str = "http://localhost:3000"

    # onlyoffice配置
    ONLYOFFICE_JWT_SECRET: str = "e39e75885d7f3688205de19c9ac041183c96624d8969dbf94d83e9da4f30feb1"
    ONLYOFFICE_SERVER_URL: str = "http://localhost:8080"


settings = Settings()
