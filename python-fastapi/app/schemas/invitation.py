"""邀请表结构(知识库/文档)"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import InvitationStatus, CollaboratorRole
from app.schemas.collaborator import CollaboratorValidInfo

class InvitationBase(BaseModel):
    """邀请基础结构(知识库/文档)"""
    token: Optional[str] = Field(default=None, description="邀请token")
    status: Optional[InvitationStatus] = Field(default=None, description="状态")
    role: Optional[CollaboratorRole] = Field(default=None, description="角色")
    need_approval: Optional[int] = Field(default=None, description="是否需要审批")

class InvitationResponse(InvitationBase):
    """邀请响应结构(知识库/文档)"""
    id: str = Field(..., description="主键")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
        
class InvitationValidInfo(BaseModel):
    """邀请信息状态(知识库/文档)"""
    knowledge_id: str = Field(..., description="所属知识库")
    status: InvitationStatus = Field(..., description="状态")
    knowledge_name: str = Field(..., description="知识库名称")
    class Config:
        from_attributes = True

class InvitationValidResponse(BaseModel):
    """邀请信息响应结构(知识库/文档)"""
    invitation: InvitationValidInfo = Field(..., description="邀请链接校验信息")
    collaborator: Optional[CollaboratorValidInfo] = Field(default=None, description="协作者校验信息")

    class Config:
        from_attributes = True