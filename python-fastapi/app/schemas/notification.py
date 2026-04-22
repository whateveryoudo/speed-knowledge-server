from pydantic import BaseModel, Field
from app.common.enums import NotificationListType, NotificationBizType
from datetime import datetime
from app.schemas.user import UserResponse
from typing import Optional, Literal


class NotificationBase(BaseModel):
    id: str = Field(..., description="通知ID")
    actor_user_id: int = Field(..., description="发起者用户id")
    mentioned_user_id: int = Field(..., description="被提及用户id")
    biz_type: NotificationBizType = Field(..., description="业务类型")
    list_type: NotificationListType = Field(..., description="列表类型")
    biz_id: str = Field(..., description="业务id")
    payload: dict = Field(..., description="负载")
    read_at: datetime = Field(default=None, description="已读时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class NotificationUpdate(NotificationBase):
    """通知更新结构"""

    read_at: Optional[datetime] = Field(default=None, description="已读时间")


class NotificationSearch(BaseModel):
    """通知搜索结构"""
    user_id: int = Field(..., description="用户id")
    list_type: Optional[NotificationListType] = Field(default=None, description="列表类型")
    type: Literal["read", "unread"] = Field(default='unread', description="已读未读")


class NotificationResponse(NotificationBase):
    """通知响应结构"""
    actor_user: UserResponse = Field(..., description="发起人")
    mentioned_user: Optional[UserResponse] = Field(default=None, description="被提及人")
    class Config:
        from_attributes = True
