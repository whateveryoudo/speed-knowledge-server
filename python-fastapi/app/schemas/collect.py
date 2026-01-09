from pydantic import BaseModel, Field
from app.common.enums import CollectResourceType
from datetime import datetime
from typing import Optional


class CollectBase(BaseModel):
    identifier: str = Field(..., description="收藏标识")
    resource_type: CollectResourceType = Field(..., description="收藏类型")

class CollectCreate(CollectBase):
    """收藏创建结构"""
    pass

class CollectSearch(BaseModel):
    """收藏搜索结构"""
    resource_type: CollectResourceType = Field(..., description="收藏类型")
    keyword: Optional[str] = Field(default=None, description="关键词")

class CollectResponse(BaseModel):
    id: str = Field(..., description="收藏ID")
    user_id: int = Field(..., description="用户ID")
    knowledge_id: Optional[str] = Field(None, description="知识ID")
    document_id: Optional[str] = Field(None, description="文档ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True