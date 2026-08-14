"""邀请表结构(知识库/文档)"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from app.common.enums import ResourceType, ResourceRole, InvitationStatus
from datetime import datetime


class ResourceInvitationJoinState(str, Enum):
    """通过邀请加入资源后的状态。"""

    APPROVAL_REQUIRED = "approval_required"
    PENDING = "pending"
    EFFECTIVE = "effective"


class ResourceInvitationCreate(BaseModel):
    """创建邀请结构"""

    resource_type: ResourceType = Field(..., description="资源类型")
    resource_id: str = Field(..., description="资源ID")
    offered_role: ResourceRole = Field(..., description="资源角色")
    need_approval: bool = Field(default=False, description="是否需要审批")


class ResourceInvitationUpdate(BaseModel):
    """更新邀请结构"""

    offered_role: Optional[ResourceRole] = Field(default=None, description="资源角色")
    need_approval: Optional[bool] = Field(default=None, description="是否需要审批")
    status: Optional[InvitationStatus] = Field(default=None, description="状态")


class ResourceInvitationResponse(BaseModel):
    """邀请响应结构"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="邀请ID")
    resource_type: ResourceType = Field(..., description="资源类型")
    resource_id: str = Field(..., description="资源ID")
    inviter_id: int = Field(..., description="邀请人ID")
    token: str = Field(..., description="邀请token")
    offered_role: ResourceRole = Field(..., description="资源角色")
    need_approval: bool = Field(default=False, description="是否需要审批")
    status: InvitationStatus = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ResourceInvitationJoinRequest(BaseModel):
    """通过邀请加入资源后的请求结构"""

    token: str = Field(..., min_length=1, max_length=64, description="邀请token")
    submit_request: bool = Field(
        default=False,
        description="是否确认提交加入申请:false为首次进入,true为开启审批需要提交申请",
    )
    apply_message: Optional[str] = Field(
        default=None, max_length=255, description="申请加入原因"
    )


class ResourceInvitationJoinResponse(BaseModel):
    """邀请响应结构"""

    state: ResourceInvitationJoinState = Field(..., description="状态")
    invitation_id: str = Field(..., description="邀请ID")
    resource_type: ResourceType = Field(..., description="资源类型")
    resource_id: str = Field(..., description="资源ID")
    resource_name: str = Field(..., description="资源名称")

    offered_role: ResourceRole = Field(..., description="资源角色")
    need_approval: bool = Field(default=False, description="是否需要审批")
    effective_role: Optional[ResourceRole] = Field(
        default=None, description="实际加入资源后的角色"
    )
    request_id: Optional[str] = Field(default=None, description="申请ID")
    grant_id: Optional[str] = Field(default=None, description="授权ID")
