"""文档结构"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from app.common.enums import DocumentType, DocumentNodeDragAction


class DocumentBase(BaseModel):
    """文档基础结构"""

    name: str = Field(..., description="文档名称", min_length=1, max_length=50)
    knowledge_id: str = Field(..., description="所属知识库ID")
    type: DocumentType = Field(..., description="文档类型")
    view_count: int = Field(default=0, description="浏览次数")
    slug: str = Field(..., description="文档短链", min_length=1, max_length=50)
    is_public: Optional[bool] = Field(default=False, description="是否公开")
    content_updated_at: Optional[datetime] = Field(
        default=None, description="内容最近更新时间"
    )


class DocumentResponse(DocumentBase):
    """文档响应结构"""

    user_id: int = Field(..., description="所属用户ID")
    id: str = Field(..., description="文档ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    has_collected: bool = Field(default=False, description="是否收藏文档")
    class Config:
        from_attributes = True


# 这里不继承基础类，需要传入的参数很少
class DocumentCreate(BaseModel):
    """创建文档结构"""

    name: str = Field(..., description="文档名称", min_length=1, max_length=50)
    knowledge_id: str = Field(..., description="所属知识库ID")
    parent_id: Optional[str] = Field(default=None, description="父节点ID")
    type: DocumentType = Field(..., description="文档类型")


class DocumentUpdate(BaseModel):
    """更新文档结构"""

    name: Optional[str] = Field(
        default=None, description="文档名称", min_length=1, max_length=50
    )
    slug: Optional[str] = Field(
        default=None, description="文档短链", min_length=1, max_length=50
    )
    trigger: Literal["outer", "editor"] = Field(
        default="outer", description="触发方式", choices=["outer", "editor"]
    )


class DragDocumentNodeParams(BaseModel):
    """拖拽文档节点参数"""

    action: DocumentNodeDragAction = Field(..., description="操作类型")
    node_id: str = Field(..., description="节点ID")
    target_id: str = Field(..., description="目标节点ID")
