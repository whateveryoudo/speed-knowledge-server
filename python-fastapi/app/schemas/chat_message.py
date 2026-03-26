from pydantic import BaseModel, Field
from datetime import datetime
from app.common.enums import ChatMessageRole, ChatMessageType
from typing import Optional
class ChatMessageBase(BaseModel):
    """聊天消息基础结构"""

    id: str = Field(..., description="消息ID")
    content: str = Field(..., description="消息内容")
    role: ChatMessageRole = Field(..., description="消息角色")
    type: ChatMessageType = Field(..., description="消息类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ChatMessageCreate(BaseModel):
    """创建聊天消息结构"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    role: ChatMessageRole = Field(..., description="消息角色")
    type: ChatMessageType = Field(..., description="消息类型")


class ChatMessageQuery(BaseModel):
    """聊天消息查询结构"""
    session_id: Optional[str] = Field(None, description="会话ID")
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")


class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应结构"""

    class Config:
        from_attributes = True
