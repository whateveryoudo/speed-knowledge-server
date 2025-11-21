"""附件结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.core.config import settings

# 这里主要是前端存储使用
class AttachmentItem(BaseModel):
    """附件信息结构"""
    id: str = Field(..., description="附件ID")
    fileName: str = Field(..., description="附件名称")
    fileType: str = Field(..., description="附件类型")
    fileSize: int = Field(..., description="附件大小")

# 默认图片(前端未传入的情况)
default_attachment_item = AttachmentItem(
    id='0567a480-0f34-4ab8-9e5d-6ab99dfcd191',
    fileName='default_cover.png',
    fileType='image/png',
    fileSize=3962
)   

class AttachmentBase(BaseModel):
    """基础附件结构(公共字段)"""

    file_name: str = Field(..., description="文件名", min_length=1, max_length=255)
    file_type: str = Field(..., description="MIME类型：如image/png, application/pdf等")
    file_size: int = Field(..., description="文件大小：字节")
    bucket_name: str = Field(..., description="存储桶名称", min_length=1, max_length=255)
    object_name: str = Field(..., description="对象键：文件在存储桶中的唯一标识", min_length=1, max_length=255)


class AttachmentResponse(AttachmentBase):
    """附件响应结构"""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentCreate(AttachmentBase):
    """创建附件结构"""
    bucket_name: Optional[str] = Field(default = settings.MINIO_BUCKET_NAME, description="存储桶名称", min_length=1, max_length=255)
    file_size: Optional[int] = Field(default = 0, description="文件大小：字节")
