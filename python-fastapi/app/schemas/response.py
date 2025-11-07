"""统一响应结构"""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

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
