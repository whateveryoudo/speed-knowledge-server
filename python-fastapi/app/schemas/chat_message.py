from token import OP
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
    link_question: Optional[str] = Field(None, description="关联问题(用于重新生成答案)")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ChatMessageCreate(BaseModel):
    """创建聊天消息结构"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    role: ChatMessageRole = Field(..., description="消息角色")
    type: ChatMessageType = Field(..., description="消息类型")
    link_question: Optional[str] = Field(None, description="关联问题(用于重新生成答案)")

class ChatMessageUpdate(BaseModel):
    """更新聊天消息结构"""
    content: Optional[str] = Field(None, description="消息内容")
    id: str = Field(..., description="消息ID")

class ChatMessageQuery(BaseModel):
    """聊天消息查询结构"""
    session_id: Optional[str] = Field(None, description="会话ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, description="每页条数")
    sort: str = Field(default="updated_at:desc", description="排序")


class ChatMessageResponse(ChatMessageBase):
    """聊天消息响应结构"""

    class Config:
        from_attributes = True
