"""文档树节点模型结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import DocumentNodeType, DocumentNodeDragAction, DocumentType


class DocumentNodeBase(BaseModel):
    """文档树节点基础结构"""

    type: DocumentNodeType = Field(..., description="文档节点类型")
    title: str = Field(..., description="文档节点标题", min_length=1, max_length=50)
    parent_id: Optional[str] = Field(
        default=None,
        description="父节点ID",
    )
    first_child_id: Optional[str] = Field(
        default=None,
        description="第一个子节点ID",
    )
    document_id: Optional[str] = Field(
        default=None, description="所属文档ID", min_length=1, max_length=50
    )
    prev_id: Optional[str] = Field(
        default=None,
        description="前一个节点ID",
    )
    next_id: Optional[str] = Field(
        default=None,
        description="下一个节点ID",
    )
    knowledge_id: str = Field(
        ..., description="所属知识库ID", min_length=1, max_length=50
    )


class DocumentNodeResponse(DocumentNodeBase):
    """文档树节点响应结构"""

    id: str = Field(..., description="文档树节点ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    document_type: Optional[DocumentType] = Field(default=None, description="所属文档类型")
    document_slug: Optional[str] = Field(default=None, description="所属文档短链")
    content_updated_at: Optional[datetime] = Field(
        default=None, description="文档内容更新时间"
    )

    class Config:
        from_attributes = True


# 这里不继承基础类，需要传入的参数很少
class DocumentNodeCreate(BaseModel):
    """创建文档目录结构"""

    id: Optional[str] = Field(default=None, description="文档ID")
    name: str = Field(..., description="文档名称", min_length=1, max_length=50)
    knowledge_id: str = Field(..., description="所属知识库ID")
    parent_id: Optional[str] = Field(default=None, description="父节点ID")
    type: DocumentNodeType = Field(..., description="文档类型")


class DocumentNodeUpdate(BaseModel):
    """更新文档节点结构"""

    title: Optional[str] = Field(default=None, description="文档节点标题", min_length=1, max_length=50)


class DragDocumentNodeParams(BaseModel):
    """拖拽文档节点参数"""

    action: DocumentNodeDragAction = Field(..., description="操作类型")
    node_id: str = Field(..., description="节点ID")
    target_id: str = Field(..., description="目标节点ID")
