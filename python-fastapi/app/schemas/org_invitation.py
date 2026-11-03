from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import OrgType, OrgInvitationUserStatus
from typing import Optional
from datetime import datetime

class OrgInvitationUpdateSettings(BaseModel):
    need_approval: Optional[bool] = Field(default=None, description="是否需要审批")
    default_dept_id: Optional[str] = Field(default=None, description="默认部门ID（仅空间邀请）")
    default_role: Optional[str] = Field(
        default=None, description="默认角色（space邀请时为空间角色，team邀请时为team角色）"
    )

class OrgInvitationResponse(BaseModel):
    id: str = Field(..., description="邀请ID")
    org_type: OrgType = Field(..., description="组织类型")
    org_id: str = Field(..., description="组织ID")
    token: str = Field(..., description="邀请凭证Token")
    need_approval: bool = Field(..., description="是否需要审批")
    default_dept_id: Optional[str] = Field(None, description="默认部门ID")
    default_role: str = Field(..., description="默认角色")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    model_config = ConfigDict(from_attributes=True)

class OrgInvitationPublicInfo(BaseModel):
    org_id: str = Field(..., description="组织ID")
    org_type: OrgType = Field(..., description="组织类型，space-空间，team-团队")
    org_icon: Optional[str] = Field(None, description="组织图标")
    org_name: Optional[str] = Field(None, description="组织名称")
    inviter_name: Optional[str] = Field(None, description="邀请人姓名")
    need_approval: bool = Field(default=False, description="是否需要审批")
    default_dept_id: Optional[str] = Field(None, description="默认部门ID（仅空间邀请）")
    default_dept_name: Optional[str] = Field(None, description="默认部门名称（仅空间邀请）")

    user_status: OrgInvitationUserStatus = Field(
        ..., description="用户在邀请组织中的状态（joined已加入、pending审批中、external外部联系人、not_joined未加入）"
    )
    org_slug: Optional[str] = Field(
        ..., 
        description="组织相关信息slug（空间下为domain,团队则为slug）"
    )

class OrgInvitationAcceptResponse(BaseModel):
    user_status: OrgInvitationUserStatus = Field(
        ..., description="用户在邀请组织中的状态（joined已加入、pending审批中、external外部联系人、not_joined未加入）"
    )
    org_id: str = Field(..., description="组织ID")
    org_slug: Optional[str] = Field(
        ..., 
        description="组织相关信息slug（空间下为domain,团队则为slug）"
    )