"""知识库分组结构"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.knowledge import KnowledgeResponse
from app.common.enums import (
    KnowledgeGroupType,
    KnowledgeGroupStyle,
)


class KnowledgeGroupDisplayConfig(BaseModel):
    """知识库分组显示配置"""

    type: KnowledgeGroupType = Field(..., description="分组类型")
    style: KnowledgeGroupStyle = Field(..., description="分组样式")
    show_knowledge_icon: Optional[bool] = Field(
        default=True, description="是否显示知识库图标"
    )
    show_knowledge_description: Optional[bool] = Field(
        default=True, description="是否显示知识库描述"
    )
    doc_order_type: Optional[int] = Field(
        default=1, description="文档排序类型:1-更新时间,2-创建时间"
    )


DEFAULT_DISPLAY_CONFIG = KnowledgeGroupDisplayConfig(
    type=KnowledgeGroupType.CARD,
    style=KnowledgeGroupStyle.DETAIL,
    show_knowledge_icon=True,
    show_knowledge_description=True,
    doc_order_type=1,
)


class KnowledgeGroupBase(BaseModel):
    """知识库分组基础结构"""

    user_id: int = Field(..., description="所属用户ID")
    group_name: str = Field(..., description="分组名称", min_length=1, max_length=50)
    order_index: int = Field(..., description="排序索引")
    is_default: Optional[bool] = Field(default=False, description="是否默认分组")
    display_config: Optional[KnowledgeGroupDisplayConfig] = Field(
        default=None, description="显示配置"
    )


class KnowledgeGroupCreate(KnowledgeGroupBase):
    """创建知识库分组"""

    pass


class KnowledgeGroupUpdateBody(BaseModel):
    """更新知识库分组（部分字段）"""

    group_name: Optional[str] = Field(
        default=None, description="分组名称", min_length=1, max_length=50
    )
    order_index: Optional[int] = Field(default=None, description="排序索引")
    display_config: Optional[KnowledgeGroupDisplayConfig] = Field(
        default=None, description="显示配置"
    )

class DocumentSummaryItem(BaseModel):
    """文档总结项(仅取一些需要显示的字段)"""
    id: str = Field(..., description="文档ID")
    name: str = Field(..., description="文档名称")
    slug: str = Field(..., description="文档短链")
    updated_at: datetime = Field(..., description="更新时间")
    content_updated_at: datetime = Field(..., description="内容更新时间")

class KnowledgeInGroupItem(KnowledgeResponse):
    """知识库分组中的知识库项(包含relation部分字段，知识库字段，文档总结前三项)"""
    order_index: int = Field(..., description="排序索引")
    relation_id: str = Field(..., description="关系ID")
    doc_summary: List[DocumentSummaryItem] = Field(..., description="文档总结(TOP3)")

class KnowledgeGroupResponse(KnowledgeGroupBase):
    """知识库分组响应"""

    id: str = Field(..., description="知识库分组ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    knowledge_group_items: Optional[List[KnowledgeInGroupItem]] = Field(
        default=None, description="知识库分组中的知识库项列表"
    )

    model_config = ConfigDict(from_attributes=True)


class KnowledgeGroupListQuery(BaseModel):
    """分组列表查询"""

    keyword: Optional[str] = Field(default=None, description="关键词")
