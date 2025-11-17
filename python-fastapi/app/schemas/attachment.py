"""附件结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.config import settings


class AttachmentBase(BaseModel):
    """基础附件结构(公共字段)"""

    file_name: str = Field(..., description="文件名", min_length=1, max_length=255)
    file_type: str = Field(..., description="MIME类型：如image/png, application/pdf等")
    file_size: int = Field(..., description="文件大小：字节")
    bucket_name: str = Field(..., description="存储桶名称", min_length=1, max_length=255)
    object_key: str = Field(..., description="对象键：文件在存储桶中的唯一标识", min_length=1, max_length=255)


class AttachmentResponse(AttachmentBase):
    """附件响应结构"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentCreate(AttachmentBase):
    """创建附件结构"""
    bucket_name: Optional[str] = Field(default = settings.MINIO_BUCKET_NAME, description="存储桶名称", min_length=1, max_length=255)
    file_size: Optional[int] = Field(default = 0, description="文件大小：字节")
