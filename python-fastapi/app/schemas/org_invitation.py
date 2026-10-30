from pydantic import BaseModel, Field, computed_field, ConfigDict
from app.common.enums import OrgType, OrgInvitationUserStatus, OrgInvitationType
from typing import List, Optional
import uuid
from datetime import datetime


class OrgInvitationUpdateSettings(BaseModel):
    need_approval: Optional[bool] = Field(default=None, description="是否需要审批")
    default_dept_id: Optional[str] = Field(default=None, description="默认部门ID（仅空间邀请）")
    default_role: Optional[str] = Field(
        default=None, description="默认角色（space邀请时为空间角色，team邀请时为team角色）"
    )


# 邀请详情（包含 Token）
class OrgInvitationWithTokenDetail(OrgInvitationDetail):
    token: str = Field(..., description="邀请凭证")


class OrginvitationPublicInfo(BaseModel):
    org_id: str = Field(..., description="组织ID")
    org_type: OrgType = Field(..., description="组织类型，space-空间，team-团队")
    org_icon: Optional[str] = Field(None, description="组织图标")
    org_name: Optional[str] = Field(None, description="组织名称")
    space_domin: Optional[str] = Field(None, description="空间域名")
    inviter_name: Optional[str] = Field(None, description="邀请人姓名")
    need_approval: bool = Field(default=False, description="是否需要审批")
    default_dept_id: Optional[str] = Field(None, description="默认部门ID（仅空间邀请）")
    default_dept_name: Optional[str] = Field(None, description="默认部门名称（仅空间邀请）")

    user_status: OrgInvitationUserStatus = Field(
        ..., description="用户在邀请组织中的状态（joined已加入、pending审批中、external外部联系人、not_joined未加入）"
    )

class OrgInvitationAcceptResponse(BaseModel):
    message: str = Field(..., description="提示消息")

    joined:bool = Field(
        ..., 
        description="是否已直接加入成功（True=直接进空间/团队，False=已提交等待审批）"
    )
    org_slug: str = Field(
        ..., 
        description="组织相关信息slug"
    )