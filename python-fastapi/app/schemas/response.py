"""统一响应结构"""

from typing import Generic, Optional, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """统一响应结构

    Args:
        BaseModel (_type_): _description_
    """

    errCode: int = 0
    errMessage: str = "success"
    success: bool = True
    data: Optional[T] = None

    @classmethod
    def success_reponse(
        cls, data: T = None, message: str = "success"
    ) -> "BaseResponse[T]":
        "成功的响应"
        return cls(errCode=0, errMessage=message, success=True, data=data)

    @classmethod
    def error_response(cls, err_code: int, err_message: str) -> "BaseResponse[None]":
        "失败的响应"
        return cls(errCode=err_code, errMessage=err_message, success=False, data=None)


class PaginationQuery(BaseModel):
    """分页查询结构"""

    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")

    @property
    def skip(self) -> int:
        """跳过条数"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """限制条数"""
        return self.page_size


class PaginationResponse(BaseModel, Generic[T]):
    """分页响应结构"""

    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")
    total: int = Field(..., description="总条数")
    items: List[T] = Field(..., description="数据列表")

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, page_size: int
    ) -> "PaginationResponse[T]":
        """创建分页响应结构"""
        return cls(page=page, page_size=page_size, total=total, items=items)
