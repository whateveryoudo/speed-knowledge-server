"""知识库分组关联结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KnowledgeGroupRelationBase(BaseModel):
    """知识库分组关联信息基础结构"""

    user_id: int = Field(..., description="所属用户ID")
    order_index: Optional[int] = Field(default=None, description="排序索引")
    knowledge_id: str = Field(..., description="知识库ID")
    group_id: str = Field(..., description="分组ID")


class KnowledgeGroupRelationCreate(KnowledgeGroupRelationBase):
    """创建知识库分组关联信息"""

    pass


class KnowledgeGroupRelationMoveBody(BaseModel):
    """移动/排序知识库分组关联"""

    group_id: str = Field(..., description="目标分组ID")
    order_index: int = Field(..., description="目标排序索引")


class KnowledgeGroupRelationResponse(KnowledgeGroupRelationBase):
    """知识库分组关联信息响应"""

    id: str = Field(..., description="关联ID")
    updated_at: datetime = Field(..., description="更新时间")
    created_at: datetime = Field(..., description="创建时间")
