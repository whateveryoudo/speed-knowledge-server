"""协作者结构"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from app.common.enums import CollaboratorRole, CollaboratorStatus, CollaboratorSource, CollaborateResourceType
from app.schemas.user import UserResponse


class CollaboratorBase(BaseModel):
    """协作者基础结构"""
    knowledge_id: Optional[str] = Field(default=None, description="所属知识库")
    document_id: Optional[str] = Field(default=None, description="所属文档")
    target_type: CollaborateResourceType = Field(..., description="目标类型")
    user_id: int = Field(..., description="所属用户")
    role: CollaboratorRole = Field(..., description="角色")
    status: CollaboratorStatus = Field(..., description="状态")
    source: CollaboratorSource = Field(..., description="来源")

class CollaboratorResponse(CollaboratorBase):
    """协作者响应结构"""
    id: str = Field(..., description="主键")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    user: Optional[UserResponse] = Field(default=None, description="用户")

class CollaboratorRequest(BaseModel):
    """协作者请求结构"""
    invitation_token: str = Field(..., description="邀请token")

class CollaboratorCreate(CollaboratorBase):
    """协作者创建结构-Route使用"""
    user_id: Optional[int] = Field(default=None, description="所属用户")
    target_type: CollaborateResourceType = Field(..., description="目标类型")
    role: Optional[CollaboratorRole] = Field(default=None, description="角色")
    status: Optional[CollaboratorStatus] = Field(default=None, description="状态")
    source: Optional[CollaboratorSource] = Field(default=None, description="来源")
class CollaboratorJoin(BaseModel):
    """协作者加入结构-Route使用"""
    invitation_token: str = Field(..., description="邀请token")
class CollaboratorUpdate(BaseModel):
    """协作者更新结构-Route使用"""
    role: Optional[CollaboratorRole] = Field(default=None, description="角色")
    status: Optional[CollaboratorStatus] = Field(default=None, description="状态")
    source: Optional[CollaboratorSource] = Field(default=None, description="来源")

class CollaboratorUpdateInfo(CollaboratorUpdate):
    """协作者更新信息结构-Service使用"""
    id: str = Field(..., description="主键")

class CollaboratorValidInfo(BaseModel):
    """协作者信息状态(这里仅返回一些用于校验的)"""
    status: CollaboratorStatus = Field(..., description="状态")

    class Config:
        from_attributes = True

class CollaboratorValidParams(BaseModel):
    """协作者获取校验信息参数"""
    user_id: int = Field(..., description="用户id")
    knowledge_id: str = Field(..., description="知识库id")
    document_id: Optional[str] = Field(default=None, description="文档id")
    resource_type: CollaborateResourceType = Field(..., description="资源类型")


class QueryPermissionGroupParams(BaseModel):
    """查询权限组参数"""
    user_id: int = Field(..., description="用户id")
    target_type: CollaborateResourceType = Field(..., description="资源类型")
    target_id: str = Field(..., description="资源id")
class CollaboratorAudit(BaseModel):
    """协作者审核结构-Route使用"""
    audit_status: Literal['agree','reject'] = Field(..., description="审核状态")