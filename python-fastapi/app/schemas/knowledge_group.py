"""知识库分组结构"""

from pydantic import BaseModel, Field
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


# 默认显示配置
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
    knowledge_items: Optional[List[KnowledgeResponse]] = Field(
        default=None, description="知识库列表"
    )


class KnowledgeGroupCreate(KnowledgeGroupBase):
    """创建知识库分组"""

    pass


class KnowledgeGroupUpdate(KnowledgeGroupBase):
    """更新知识库分组"""

    id: int = Field(..., description="知识库分组ID")
    group_name: Optional[str] = Field(
        default=None, description="分组名称", min_length=1, max_length=50
    )
    order_index: Optional[int] = Field(default=None, description="排序索引")
    display_config: Optional[KnowledgeGroupDisplayConfig] = Field(
        default=None, description="显示配置"
    )


class KnowledgeGroupResponse(KnowledgeGroupBase):
    """知识库分组响应"""

    id: str = Field(..., description="知识库分组ID")
