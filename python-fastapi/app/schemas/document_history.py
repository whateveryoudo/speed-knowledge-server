from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.common.enums import DocumentType, DocumentHistoryType, DocumentCreatorScope


class DocumentHistoryQuery(BaseModel):
    """文档历史查询结构"""

    doc_name: Optional[str] = Field(
        default=None,
        description="文档名称",
    )

    doc_creator_scope: DocumentCreatorScope = Field(
        default=DocumentCreatorScope.ALL,
        description="创建者范围：all-所有，mine-我创建的",
    )

    doc_type: Optional[DocumentType] = Field(
        default=None,
        description="文档类型",
    )
    doc_belong_knowledge_id: Optional[str] = Field(None, description="知识库ID")
    history_type: DocumentHistoryType = Field(..., description="历史列表类型")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页条数")


class DocumentHistoryResponse(BaseModel):
    """文档历史响应结构（这里会组合一些用户信息和文档信息）"""

    id: str = Field(..., description="主键")
    doc_id: str = Field(..., description="文档ID")
    doc_name: str = Field(..., description="文档名称")
    doc_slug: str = Field(..., description="文档短链")
    doc_creator: str = Field(..., description="文档创建者")
    doc_type: DocumentType = Field(..., description="文档类型")
    doc_is_collected: bool = Field(..., description="是否已收藏")
    doc_belong_knowledge_id: str = Field(
        ...,
        description="所属知识库ID",
    )
    doc_belong_knowledge_name: str = Field(
        ...,
        description="所属知识库名称",
    )
    doc_belong_knowledge_slug: str = Field(
        ...,
        description="所属知识库短链",
    )

    doc_belong_space_id: str = Field(
        ...,
        description="所属空间ID",
    )

    doc_belong_team_slug: Optional[str] = Field(
        default=None,
        description="所属团队短链",
    )
    doc_belong_team_name: Optional[str] = Field(
        default=None,
        description="所属团队名称",
    )
    update_datetime: datetime = Field(..., description="更新时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
