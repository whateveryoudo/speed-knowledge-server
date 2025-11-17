"""Minio 客户端"""

from typing import Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MinioClient:
    """Minio 客户端单例"""

    _instance: Optional[Minio] = None

    @classmethod
    def get_client(cls) -> Minio:
        if cls._instance is None:
            try:
                cls._instance = Minio(
                    endpoint=settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_USE_SSL,
                )
                bucket = settings.MINIO_BUCKET_NAME
                if not cls._instance.bucket_exists(bucket):
                    cls._instance.make_bucket(bucket)
            except S3Error as exec:
                logger.exception("初始化 minio 失败: %s", exec)
                raise RuntimeError("初始化 minio 失败") from exec
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """关闭 Minio 链接"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


def get_minio() -> Minio:
    return MinioClient.get_client()
