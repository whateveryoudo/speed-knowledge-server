from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.common.enums import DocumentType, DocumentHistoryType

class DocumentHistoryQueryBase(BaseModel):
    """文档历史查询基础(浏览/编辑/点赞/收藏)"""
    doc_name: Optional[str] = Field(None, description="文档名称")
    doc_belong_knowledge_name: Optional[str] = Field(None, description="知识库名称")
    doc_creator: Optional[str] = Field(None, description="文档创建者")
    doc_type: Optional[DocumentType] = Field(None, description="文档类型")
    doc_belong_knowledge_id: Optional[str] = Field(None, description="知识库ID")
    doc_belong_knowledge_slug: Optional[str] = Field(None, description="知识库短链")

class DocumentHistoryQuery(DocumentHistoryQueryBase):
    """文档历史查询结构"""
    user_id: Optional[int] = Field(None, description="用户ID")
    doc_belong_knowledge_id: Optional[str] = Field(None, description="知识库ID")
    history_type: DocumentHistoryType = Field(..., description="历史列表类型")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")

class DocumentHistoryResponse(DocumentHistoryQueryBase):
    """文档历史响应结构（这里会组合一些用户信息和文档信息）"""
    id: str = Field(..., description="主键")
    doc_slug: str = Field(..., description="文档短链")
    doc_is_collected: bool = Field(..., description="是否已收藏")
    update_datetime: datetime = Field(..., description="更新时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")