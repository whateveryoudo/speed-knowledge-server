"""Redis 客户端"""
import redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    """Redis 客户端单例"""

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取 Redis 客户端实例"""
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=settings.REDIS_DECODE_RESPONSES
            )
        return cls._instance

    @classmethod
    def close(cls):
        """关闭 Redis 连接"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


def get_redis() -> redis.Redis:
    """获取 Redis 客户端"""
    return RedisClient.get_client();


