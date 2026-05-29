"""分页工具函数"""

from typing import List, Sequence, Tuple, TypeVar

from sqlalchemy.orm import Query

from app.schemas.response import PaginationQuery, PaginationResponse

T = TypeVar("T")


def paginate_query(
    query: Query, pagination_query: PaginationQuery
) -> Tuple[List[T], int, bool]:
    """分页查询，返回数据列表和总条数"""
    total = query.count()
    items = query.offset(pagination_query.skip).limit(pagination_query.limit).all()
    # 返回给前端使用
    has_more = total > pagination_query.skip + pagination_query.limit
    return items, total, has_more


def paginate_after_fetch(
    items: Sequence[T],
    total: int,
    pagination_query: PaginationQuery,
) -> Tuple[List[T], int, bool]:
    """
    原生 SQL / DDL 等已得到当前页 ``items`` 与总条数 ``total`` 时，
    计算 ``has_more``，返回与 :func:`paginate_query` 相同形状的三元组。
    """
    total_i = int(total)
    has_more = total_i > pagination_query.skip + pagination_query.limit
    return list(items), total_i, has_more


def paginate_response(
    items: List[T], total: int, has_more: bool, pagination_query: PaginationQuery
) -> PaginationResponse[T]:
    """分页响应，返回分页响应结构"""
    return PaginationResponse.create(
        items, total, has_more, pagination_query.page, pagination_query.page_size
    )
