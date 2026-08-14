from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import ResourceType, ResourceRole, AccessRequestStatus
from datetime import datetime
from typing import Optional
from app.schemas.query import Pagination


class AccessRequestUserResponse(BaseModel):
    """审批列表用户简要信息"""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")


class ResourceAccessRequestResponse(BaseModel):
    """资源访问申请响应"""

    model_config = ConfigDict(from_attributes=True)
    id: str = Field(..., description="ID")
    resource_id: str = Field(..., description="资源ID")
    resource_type: ResourceType = Field(..., description="资源类型")
    requested_role: ResourceRole = Field(..., description="资源角色")

    status: AccessRequestStatus = Field(..., description="申请状态")
    apply_message: Optional[str] = Field(None, description="申请备注")

    reviewed_by: Optional[int] = Field(None, description="审批人ID")
    reviewed_at: Optional[datetime] = Field(None, description="审批时间")
    applicant_user_id: int = Field(..., description="申请人ID")
    invitation_id: Optional[str] = Field(None, description="邀请ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ResourceAccessRequestListItem(ResourceAccessRequestResponse):
    """审批列表项，附带申请人和审批人信息"""

    applicant: AccessRequestUserResponse = Field(..., description="申请人")
    reviewed_user: Optional[AccessRequestUserResponse] = Field(
        None, description="审批人信息"
    )


class ResourceAccessRequestQuery(Pagination):
    """资源访问申请列表请求参数"""

    status: Optional[AccessRequestStatus] = Field(None, description="申请状态")
