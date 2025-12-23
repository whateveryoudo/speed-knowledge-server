"""文档树节点模型结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import DocumentNodeType


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
    document_id: str = Field(..., description="所属文档ID", min_length=1, max_length=50)
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
    document_slug: Optional[str] = Field(default=None, description="所属文档短链")

    class Config:
        from_attributes = True
