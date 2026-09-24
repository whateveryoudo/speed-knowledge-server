"""知识库结构"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, List
from datetime import datetime
from app.schemas.attachment import AttachmentItem
from app.common.enums import (
    KnowledgeIndexPageLayout,
    KnowledgeIndexPageSort,
    KnowledgeFromWay,
    KnowledgeAbility,
    DocumentAbility,
    KnowledgeScopeType,
    KnowledgeVisibility,
)
from app.schemas.team import TeamResponse
from app.schemas.query import BasePaginationQuery


class KnowledgeBase(BaseModel):
    """知识库基础结构"""

    creator_id: int = Field(..., description="用户ID")
    icon: Optional[str] = Field(default="icon-book-0", description="知识库图标")
    name: str = Field(..., description="知识库名称", min_length=1, max_length=50)
    slug: str = Field(..., description="知识库短链", min_length=1, max_length=50)
    team_id: Optional[str] = Field(default=None, description="所属团队")
    space_id: str = Field(..., description="所属空间")
    description: Optional[str] = Field(
        default=None, description="知识库描述", max_length=250
    )
    cover_url: Optional[AttachmentItem] = Field(default=None, description="封面图URL")
    visibility: Optional[KnowledgeVisibility] = Field(
        default=None,
        description="公开范围:private私有, space空间成员可见, public互联网公开,替换之前的is_public字段",
    )
    items_count: Optional[int] = Field(default=0, description="文档数量")
    content_updated_at: Optional[datetime] = Field(
        default=None, description="内容最近更新时间"
    )


class KnowledgeVisibilityUpdate(BaseModel):
    """知识库公开范围更新结构"""

    visibility: KnowledgeVisibility = Field(
        ...,
        description="公开范围:private私有, space空间成员可见, public互联网公开,替换之前的is_public字段",
    )


class KnowledgeListQuery(BasePaginationQuery):
    """知识库列表查询结构(继承自基础分页查询结构)"""

    keyword: Optional[str] = Field(None, description="关键词")
    scope: KnowledgeFromWay = Field(
        default=KnowledgeFromWay.OWN, description="查询范围"
    )


class KnowledgeListMineQuery(BasePaginationQuery):
    """我的知识库列表查询结构(继承自基础分页查询结构)"""

    keyword: Optional[str] = Field(None, description="关键词")
    abilities: Optional[List[Union[KnowledgeAbility, DocumentAbility]]] = Field(
        None, description="要求知识库具备的全部能力"
    )


class KnowledgeResponse(KnowledgeBase):
    """知识库响应结构"""

    creator_id: int = Field(..., description="所属用户ID")
    id: str = Field(..., description="知识库ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    team: Optional[TeamResponse] = Field(default=None, description="所属团队")
    source: Optional[KnowledgeFromWay] = Field(default=None, description="知识库来源：自己创建的、参与协同的")
    scope_slug: Optional[str] = Field(
        default=None, description="路由作用域短链：username / public_area_slug / team.slug"
    )
    ability: Optional[Dict[Union[KnowledgeAbility, DocumentAbility], bool]] = Field(
        default=None, description="知识库权限能力"
    )

    class Config:
        from_attributes = True


class KnowledgeRouteContext(BaseModel):
    """知识库路由上下文"""

    knowledge_id: str = Field(..., description="知识库ID")
    knowledge_name: str = Field(..., description="知识库名称")
    knowledge_slug: str = Field(..., description="知识库短链")
    team_id: Optional[str] = Field(default=None, description="所属团队ID")
    team_name: Optional[str] = Field(default=None, description="所属团队名称")
    team_slug: Optional[str] = Field(default=None, description="所属团队短链")
    scope_type: KnowledgeScopeType = Field(..., description="知识库范围类型")
    space_id: str = Field(..., description="所属空间ID")
    space_domain: str = Field(..., description="所属空间域名")
    scope_slug: str = Field(..., description="替代之前的team_slug")


class KnowledgeCreate(KnowledgeBase):
    """创建知识库结构"""

    creator_id: Optional[int] = Field(default=None, description="所属用户ID")
    group_id: Optional[str] = Field(default=None, description="所属分组ID")
    team_id: Optional[str] = Field(default=None, description="所属团队ID")
    slug: Optional[str] = Field(
        default=None, description="知识库短链", min_length=1, max_length=50
    )


class KnowledgeUpdate(BaseModel):
    """更新知识库结构"""

    name: Optional[str] = Field(
        default=None, description="知识库名称", min_length=1, max_length=50
    )
    slug: Optional[str] = Field(
        default=None, description="知识库短链", min_length=1, max_length=50
    )
    description: Optional[str] = Field(
        default=None, description="知识库描述", max_length=250
    )
    cover_url: Optional[AttachmentItem] = Field(default=None, description="封面图URL")


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
    has_collected: Optional[bool] = Field(default=None, description="是否已收藏")

    class Config:
        from_attributes = True
