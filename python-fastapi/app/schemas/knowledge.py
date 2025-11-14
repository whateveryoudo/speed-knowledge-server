"""知识库结构"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class KnowledgeBase(BaseModel):
    """知识库基础结构"""
    user_id: str = Field(..., description="所属用户ID")
    name: str = Field(..., description="知识库名称", min_length=1, max_length=50)
    slug: str = Field(..., description="知识库短链", min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, description="知识库描述", min_length=1, max_length=250)
    cover_url: Optional[str] = Field(default=None, description="封面图URL")
    is_public: Optional[bool] = Field(default=False, description="是否公开")
    items_count: Optional[int] = Field(default=0, description="文档数量")
    content_updated_at: Optional[datetime] = Field(default=None, description="内容最近更新时间")
   
class KnowledgeResponse(KnowledgeBase):
    """知识库响应结构"""
    id: int = Field(..., description="知识库ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class KnowledgeCreate(KnowledgeBase):
    """创建知识库结构"""
    pass

class KnowledgeUpdate(KnowledgeBase):
    """更新知识库结构"""
    id: int = Field(..., description="知识库ID")
    user_id: Optional[str] = Field(default=None, description="所属用户ID")
    name: Optional[str] = Field(default=None, description="知识库名称", min_length=1, max_length=50)
    slug: Optional[str] = Field(default=None, description="知识库短链", min_length=1, max_length=50)