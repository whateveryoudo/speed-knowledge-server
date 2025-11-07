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

    # jwt 
    SECRET_KEY:str='fa44273b1571628e36b527acabe1c06d796fad30cbb4ac40c93fdb10a30bb90f'
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

settings = Settings()
