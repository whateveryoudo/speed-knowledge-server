"""分页工具函数"""

from typing import List, Generic, Tuple, TypeVar
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query
from app.schemas.response import PaginationQuery, PaginationResponse

T = TypeVar("T")


def paginate_query(
    query: Query, pagination_query: PaginationQuery
) -> Tuple[List[T], int]:
    """分页查询，返回数据列表和总条数"""
    total = query.count()
    items = query.offset(pagination_query.skip).limit(pagination_query.limit).all()

    return items, total


def paginate_response(
    items: List[T], total: int, pagination_query: PaginationQuery
) -> PaginationResponse[T]:
    """分页响应，返回分页响应结构"""
    return PaginationResponse.create(
        items, total, pagination_query.page, pagination_query.page_size
    )
