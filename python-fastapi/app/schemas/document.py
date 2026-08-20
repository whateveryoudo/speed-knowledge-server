"""文档结构"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from app.common.enums import DocumentType, DocumentExportFormat, DocumentVisibility


class DocumentBase(BaseModel):
    """文档基础结构"""

    name: str = Field(..., description="文档名称", min_length=1, max_length=50)
    knowledge_id: str = Field(..., description="所属知识库ID")
    type: DocumentType = Field(..., description="文档类型")
    view_count: int = Field(default=0, description="浏览次数")
    slug: str = Field(..., description="文档短链", min_length=1, max_length=50)
    visibility: DocumentVisibility = Field(
        default=DocumentVisibility.INHERIT, description="文档可见类别"
    )
    content_updated_at: Optional[datetime] = Field(
        default=None, description="内容最近更新时间"
    )


class DocumentResponse(DocumentBase):
    """文档响应结构"""

    user_id: int = Field(..., description="所属用户ID")
    id: str = Field(..., description="文档ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    has_collected: Optional[bool] = Field(default=False, description="是否收藏文档")

    class Config:
        from_attributes = True


class DocumentRouteContext(BaseModel):
    """文档路由上下文"""

    document_id: str = Field(..., description="文档ID")
    document_name: str = Field(..., description="文档名称")
    document_slug: str = Field(..., description="文档短链")
    knowledge_id: str = Field(..., description="所属知识库ID")
    knowledge_name: str = Field(..., description="知识库名称")
    knowledge_slug: str = Field(..., description="知识库短链")
    team_id: Optional[str] = Field(default=None, description="所属团队ID")
    team_name: Optional[str] = Field(default=None, description="团队名称")
    team_slug: Optional[str] = Field(default=None, description="团队短链")
    space_id: str = Field(..., description="所属空间ID")
    space_domain: Optional[str] = Field(default=None, description="空间域名")
    scope_slug: str = Field(..., description="替代之前的team_slug")


class DocumentCreate(BaseModel):
    """创建文档结构"""

    user_id: Optional[int] = Field(default=None, description="所属用户ID")
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


class DocumentVisibilityUpdate(BaseModel):
    """文档公开范围更新"""

    visibility: DocumentVisibility = Field(
        ...,
        description=(
            "inherit继承知识库范围；"
            "private关闭父级空间/公开入口；"
            "space对空间内部成员开放；"
            "public对互联网公开"
        ),
    )


class DocumentExportRequest(BaseModel):
    """文档导出请求"""

    format: DocumentExportFormat = Field(..., description="导出格式")
