from app.common.enums.search import SearchContextType, SearchVisibilityType
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Union


class SearchQuery(BaseModel):
    context: SearchContextType = Field(..., description="搜索上下文:看板/外部=global，库内=knowledge")
    visibility: SearchVisibilityType = Field(..., description="搜索可见性：与我相关|公开")
    keyword: str = Field(..., description="搜索关键词")
    knowledge_id: Optional[str] = Field(None, description="知识库ID， 当在知识库内部搜索时，必须传入知识库id")

    @model_validator(mode="after")
    def validate_context(self):
        """验证搜索上下文(当在知识库内部搜索时，必须传入知识库id)"""
        if self.context == SearchContextType.KNOWLEDGE and not self.knowledge_id:
            raise ValueError("knowledge_id is required when context is KNOWLEDGE")
        return self


class SearchKnowledgeItem(BaseModel):
    id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    slug: str = Field(..., description="知识库slug")
    team_slug: Optional[str] = Field(None, description="团队slug")
    is_public: bool = Field(..., description="是否公开")


class SearchDocumentItem(BaseModel):
    id: str = Field(..., description="文档ID")
    name: str = Field(..., description="文档名称")
    slug: str = Field(..., description="文档slug")
    knowledge_id: str = Field(..., description="知识库ID")
    knowledge_name: str = Field(..., description="知识库名称")
    knowledge_slug: str = Field(..., description="知识库slug")
    team_slug: Optional[str] = Field(None, description="团队slug")


class SearchSection(BaseModel):
    type: str
    items: List[Union[SearchKnowledgeItem, SearchDocumentItem]]


class SearchResponse(BaseModel):
    sections: List[SearchSection]
