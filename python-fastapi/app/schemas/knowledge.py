"""知识库结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.attachment import AttachmentItem
from app.common.enums import KnowledgeIndexPageLayout, KnowledgeIndexPageSort


class KnowledgeBase(BaseModel):
    """知识库基础结构"""

    icon: str = Field(default="icon-book-0", description="知识库图标")
    name: str = Field(..., description="知识库名称", min_length=1, max_length=50)
    slug: str = Field(..., description="知识库短链", min_length=1, max_length=50)
    group_id: str = Field(..., description="所属分组")
    description: Optional[str] = Field(
        default=None, description="知识库描述", min_length=1, max_length=250
    )
    cover_url: Optional[AttachmentItem] = Field(default=None, description="封面图URL")
    is_public: Optional[bool] = Field(default=False, description="是否公开")
    items_count: Optional[int] = Field(default=0, description="文档数量")
    content_updated_at: Optional[datetime] = Field(
        default=None, description="内容最近更新时间"
    )


class KnowledgeResponse(KnowledgeBase):
    """知识库响应结构"""

    user_id: int = Field(..., description="所属用户ID")
    id: str = Field(..., description="知识库ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class KnowledgeCreate(KnowledgeBase):
    """创建知识库结构"""

    slug: Optional[str] = Field(
        default=None, description="知识库短链", min_length=1, max_length=50
    )


class KnowledgeUpdate(KnowledgeBase):
    """更新知识库结构"""

    id: str = Field(..., description="知识库ID")
    user_id: Optional[int] = Field(default=None, description="所属用户ID")
    name: Optional[str] = Field(
        default=None, description="知识库名称", min_length=1, max_length=50
    )
    slug: Optional[str] = Field(
        default=None, description="知识库短链", min_length=1, max_length=50
    )

class KnowledgeFullResponse(KnowledgeResponse):
    """知识库完整响应结构"""

    enable_catalog: bool = Field(..., description="是否启用目录")
    enable_custom_body: bool = Field(..., description="是否启用自定义模块")
    enable_user_feed: bool = Field(..., description="是否显示协同人员")
    layout: KnowledgeIndexPageLayout = Field(..., description="布局")
    sort: KnowledgeIndexPageSort = Field(..., description="排序")
    class Config:
        from_attributes = True

class KnowledgeIndexPageResponse(KnowledgeFullResponse):
    """知识库首页信息结构"""

    word_count: int = Field(..., description="文档字数")
    has_collected: bool = Field(..., description="是否已收藏")
    class Config:
        from_attributes = True