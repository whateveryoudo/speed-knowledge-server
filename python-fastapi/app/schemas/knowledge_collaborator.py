"""协作者结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import KnowledgeCollaboratorRole, KnowledgeCollaboratorStatus, KnowledgeCollaboratorSource
from app.schemas.user import UserResponse


class KnowledgeCollaboratorBase(BaseModel):
    """协作者基础结构"""
    knowledge_id: str = Field(..., description="所属知识库")
    user_id: int = Field(..., description="所属用户")
    role: KnowledgeCollaboratorRole = Field(..., description="角色")
    status: KnowledgeCollaboratorStatus = Field(..., description="状态")
    source: KnowledgeCollaboratorSource = Field(..., description="来源")

class KnowledgeCollaboratorResponse(KnowledgeCollaboratorBase):
    """协作者响应结构"""
    id: str = Field(..., description="主键")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    user: Optional[UserResponse] = Field(default=None, description="用户")

class KnowledgeCollaboratorRequest(BaseModel):
    """协作者请求结构"""
    invitation_token: str = Field(..., description="邀请token")

class KnowledgeCollaboratorCreate(KnowledgeCollaboratorBase):
    """协作者创建结构"""
    user_id: Optional[int] = Field(default=None, description="所属用户")
    role: Optional[KnowledgeCollaboratorRole] = Field(default=None, description="角色")
    status: Optional[KnowledgeCollaboratorStatus] = Field(default=None, description="状态")
    source: Optional[KnowledgeCollaboratorSource] = Field(default=None, description="来源")

class KnowledgeCollaboratorValidInfo(BaseModel):
    """协作者信息状态(这里仅返回一些用于校验的)"""
    status: KnowledgeCollaboratorStatus = Field(..., description="状态")

    class Config:
        from_attributes = True

class KnowledgeCollaboratorValidParams(BaseModel):
    """协作者获取校验信息参数"""
    user_id: int = Field(..., description="所属用户")
    knowledge_id: str = Field(..., description="所属知识库")