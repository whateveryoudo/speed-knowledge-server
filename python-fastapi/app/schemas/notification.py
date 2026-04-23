from pydantic import BaseModel, Field
from app.common.enums import NotificationListType, NotificationBizType
from datetime import datetime
from app.schemas.user import UserResponse
from typing import Optional, Literal
from app.common.validator import FlexibleOptional


class NotificationBase(BaseModel):
    id: str = Field(..., description="通知ID")
    actor_user_id: int = Field(..., description="发起者用户id")
    mentioned_user_id: int = Field(..., description="被提及用户id")
    biz_type: NotificationBizType = Field(..., description="业务类型")
    list_type: NotificationListType = Field(..., description="列表类型")
    biz_id: str = Field(..., description="业务id")
    payload: dict = Field(..., description="负载")
    read_at: Optional[datetime] = Field(default=None, description="已读时间")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")


class NotificationUpdate(NotificationBase):
    """通知更新结构"""

    read_at: Optional[datetime] = Field(default=None, description="已读时间")


class NotificationSearch(BaseModel):
    """通知搜索结构"""

    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")
    user_id: Optional[int] = Field(default=None, description="用户id")
    list_type: FlexibleOptional[NotificationListType] = Field(
        default=None, description="列表类型"
    )
    type: Literal["read", "unread"] = Field(default="unread", description="已读未读")


class NotificationResponse(NotificationBase):
    """通知响应结构"""

    actor_user: UserResponse = Field(..., description="发起人")
    mentioned_user: Optional[UserResponse] = Field(default=None, description="被提及人")

    class Config:
        from_attributes = True
