from pydantic import BaseModel, Field
from app.common.enums import CollectResourceType, DocumentType
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

    resource_type: Optional[CollectResourceType] = Field(
        default=None, description="收藏类型，不传表示全部"
    )
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


class CollectTeamBrief(BaseModel):
    """收藏团队简要信息"""

    name: str = Field(..., description="团队名称")
    slug: str = Field(..., description="团队短链")


class CollectKnowledgeBrief(BaseModel):
    """收藏知识简要信息"""

    name: str = Field(..., description="知识库名称")
    slug: str = Field(..., description="知识库短链")
    icon: str = Field(..., description="知识库图标")
    id: str = Field(..., description="知识库ID")


class CollectDocumentBrief(BaseModel):
    """收藏文档简要信息"""

    name: str = Field(..., description="文档名称")
    slug: str = Field(..., description="文档短链")
    id: str = Field(..., description="文档ID")
    type: DocumentType = Field(..., description="文档类型")


class CollectListItemResponse(BaseModel):
    """收藏列表项"""

    id: str = Field(..., description="收藏ID")
    resource_type: CollectResourceType = Field(..., description="收藏类型")
    identifier: str = Field(..., description="取消收藏用的资源ID")
    created_at: datetime = Field(..., description="收藏时间")
    team: CollectTeamBrief
    knowledge: CollectKnowledgeBrief
    document: Optional[CollectDocumentBrief] = Field(None, description="文档简要信息")
