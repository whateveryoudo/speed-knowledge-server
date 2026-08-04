"""邀请表结构(知识库/文档)"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from app.common.enums import ResourceType, ResourceRole


class InvitationJoinState(str, Enum):
    """通过邀请加入资源后的状态。"""

    APPROVAL_REQUIRED = "approval_required"
    PENDING = "pending"
    EFFECTIVE = "effective"


class InvitationJoinRequest(BaseModel):
    """通过邀请加入资源后的请求结构"""

    token: Optional[str] = Field(default=None, description="邀请token")
    submit_request: bool = Field(
        default=False,
        description="是否确认提交加入申请:false为首次进入,true为开启审批需要提交申请",
    )
    apply_message: Optional[str] = Field(
        default=None, max_length=500, description="申请加入原因"
    )


class InvitationJoinResponse(BaseModel):
    """邀请响应结构"""

    state: InvitationJoinState = Field(..., description="状态")
    invitation_id: str = Field(default=None, description="邀请ID")
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
