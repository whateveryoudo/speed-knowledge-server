"""知识库邀请表结构"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import KnowledgeInvitationStatus, KnowledgeCollaboratorRole
from app.schemas.knowledge_collaborator import KnowledgeCollaboratorValidInfo

class KnowledgeInvitationBase(BaseModel):
    """知识库邀请基础结构"""
    token: Optional[str] = Field(default=None, description="邀请token")
    status: Optional[KnowledgeInvitationStatus] = Field(default=None, description="状态")
    role: Optional[KnowledgeCollaboratorRole] = Field(default=None, description="角色")
    need_approval: Optional[int] = Field(default=None, description="是否需要审批")

class KnowledgeInvitationResponse(KnowledgeInvitationBase):
    """知识库邀请响应结构"""
    id: str = Field(..., description="主键")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
        
class KnowledgeInvitationValidInfo(BaseModel):
    """邀请信息状态"""
    knowledge_id: str = Field(..., description="所属知识库")
    status: KnowledgeInvitationStatus = Field(..., description="状态")
    knowledge_name: str = Field(..., description="知识库名称")
    class Config:
        from_attributes = True

class KnowledgeInvitationValidResponse(BaseModel):
    """邀请信息响应结构"""
    invitation: KnowledgeInvitationValidInfo = Field(..., description="邀请链接校验信息")
    collaborator: Optional[KnowledgeCollaboratorValidInfo] = Field(default=None, description="协作者校验信息")

    class Config:
        from_attributes = True