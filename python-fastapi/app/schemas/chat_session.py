from langgraph.store.base import Op
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.common.enums.chat import ChatSessionStatus


class ChatSessionBase(BaseModel):
    """聊天会话基础结构"""

    id: str = Field(..., description="主键")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="会话标题")
    last_message_preview: Optional[str] = Field(
        None, description="最后一条消息预览(摘要)"
    )

    status: ChatSessionStatus = Field(..., description="会话状态")

class ChatSessionUpdate(BaseModel):
    """更新聊天会话结构"""
    title: Optional[str] = Field(None, description="会话标题")
    status: Optional[ChatSessionStatus] = Field(None, description="会话状态")
    last_message_preview: Optional[str] = Field(None, description="最后一条消息预览(摘要)")
    
class ChatSessionQuery(BaseModel):
    """聊天会话查询结构"""
    title: Optional[str] = Field(None, description="会话标题")
    status: Optional[ChatSessionStatus] = Field(None, description="会话状态")
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页条数")

class ChatSessionFullQuery(ChatSessionQuery):
    """聊天会话查询结构(包含已删除的数据)"""
    user_id: int = Field(..., description="用户ID")

class ChatSessionCreate(ChatSessionBase):
    """创建聊天会话结构"""
    id: str = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., description="会话标题")
    status: ChatSessionStatus = Field(..., description="会话状态")


class ChatSessionResponse(ChatSessionBase):
    """聊天消息响应结构"""

    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
