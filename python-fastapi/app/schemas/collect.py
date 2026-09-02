from pydantic import BaseModel, Field
from app.common.enums import DocumentType, CollectTargetType
from datetime import datetime
from typing import Optional




class CollectCreate(BaseModel):
    """收藏创建结构"""

    target_type: CollectTargetType = Field(..., description="目标资源类型")
    target_id: str = Field(..., description="目标资源ID")


class CollectSearch(BaseModel):
    """收藏搜索结构"""

    target_type: Optional[CollectTargetType] = Field(
        default=None, description="目标类型，不传表示全部"
    )
    keyword: Optional[str] = Field(default=None, description="关键词")


class CollectResponse(BaseModel):
    id: str = Field(..., description="收藏ID")
    user_id: int = Field(..., description="用户ID")
    target_type: CollectTargetType = Field(..., description="目标类型")
    target_id: str = Field(..., description="目标ID")
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
    target_type: CollectTargetType = Field(..., description="目标资源类型")
    target_id: str = Field(..., description="目标资源ID")
    created_at: datetime = Field(..., description="收藏时间")
    team: Optional[CollectTeamBrief] = Field(None, description="团队简要信息")
    knowledge: Optional[CollectKnowledgeBrief] = Field(None, description="知识简要信息")
    document: Optional[CollectDocumentBrief] = Field(None, description="文档简要信息")
