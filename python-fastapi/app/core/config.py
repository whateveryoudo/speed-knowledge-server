from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    APP_NAME: str = "FastAPI Server"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8005
    DEBUG: bool = True

    # Redis配置

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_DECODE_RESPONSES: bool = True

    # 数据库配置
    DATABASE_URL:str = "mysql+pymysql://root:onemoretime123.@localhost:3306/speed-knowledge"


settings = Settings()
