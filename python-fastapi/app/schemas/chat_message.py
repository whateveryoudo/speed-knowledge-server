from token import OP
from pydantic import BaseModel, Field
from datetime import datetime
from app.common.enums import ChatMessageRole, ChatMessageType
from typing import Optional, List
class ChatMessageBase(BaseModel):
    """聊天消息基础结构"""

    id: str = Field(..., description="消息ID")
    content: str = Field(..., description="消息内容")
    role: ChatMessageRole = Field(..., description="消息角色")
    type: ChatMessageType = Field(..., description="消息类型")
    context_json: Optional[dict] = Field(None, description="上下文json(用于缓存一些替换的上下文)")
    link_question: Optional[str] = Field(None, description="关联问题(用于重新生成答案)")
    answer_group_id: str = Field(..., description="答案组ID")
    version: int = Field(..., description="版本")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """创建聊天消息结构"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    role: ChatMessageRole = Field(..., description="消息角色")
    type: ChatMessageType = Field(..., description="消息类型")
    context_json: Optional[dict] = Field(None, description="上下文json(用于缓存一些替换的上下文)")
    link_question: Optional[str] = Field(None, description="关联问题(用于重新生成答案)")
    answer_group_id: Optional[str] = Field(None, description="答案组ID")
    version: Optional[int] = Field(None, description="版本")

class ChatMessageUpdate(BaseModel):
    """更新聊天消息结构"""
    content: Optional[str] = Field(None, description="消息内容")
    answer_group_id: str = Field(..., description="答案组ID")
    context_json: Optional[dict] = Field(None, description="上下文json(用于缓存一些替换的上下文)")
class ChatMessageQuery(BaseModel):
    """聊天消息查询结构"""
    session_id: Optional[str] = Field(None, description="会话ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, description="每页条数")
    sort: str = Field(default="updated_at:desc", description="排序")


class ChatMessageResponse(BaseModel):
    """聊天消息响应结构"""
    answer_group_id: str = Field(..., description="分组id")
    sub_messages: List[ChatMessageBase] = Field(..., description="子消息列表")
    class Config:
        from_attributes = True
