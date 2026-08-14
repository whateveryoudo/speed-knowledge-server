from pydantic import BaseModel, Field
from app.common.enums import BaseSortOrder
from typing import Optional, List


class SortRule(BaseModel):
    """基础排序规则结构"""

    field: str = Field(..., description="排序字段")
    order: BaseSortOrder = Field(default=BaseSortOrder.ASC, description="排序顺序")


class Pagination(BaseModel):
    """基础分页查询结构"""

    page: int = Field(default=1,ge=1, description="页码")
    page_size: int = Field(default=10,ge=1,le=100, description="每页条数")


class BasePaginationQuery(Pagination):
    """基础查询结构(主要是分页和排序的通用结构)"""

    sorts: Optional[List[SortRule]] = Field(None, description="排序")
