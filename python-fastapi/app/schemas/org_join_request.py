from app.schemas.user import UserBrief
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import OrgType, ApprovalStatus
from typing import Optional
from datetime import datetime

class OrgJoinRequestItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:str = Field(..., description="")
    org_id:str = Field(..., description="")
    org_type:OrgType = Field(..., description="")
    org_name: str = Field(default=None, description="组织名称")
    applicant_user: UserBrief = Field(..., description="申请人信息")
    status:ApprovalStatus = Field(..., description="申请状态:pending-待处理，approved-已批准，rejected-已拒绝")
    department_id:Optional[str] = Field(default=None, description="申请部门ID")
    department_name:Optional[str] = Field(default=None, description="申请部门名称")
    apply_message:Optional[str] = Field(default=None, description="申请附言")
    reviewed_by:Optional[UserBrief] = Field(default=None, description="审核人")
    reviewed_at:Optional[datetime] = Field(default=None, description="审核时间")
    created_at: datetime = Field(..., description="申请创建时间")

class OrgJoinRequestQuery(BaseModel):
    status:Optional[ApprovalStatus] = Field(default=None, description="申请状态:pending-待处理，approved-已批准，rejected-已拒绝,默认是全部")

class OrgJoinRequestAudit(BaseModel):
    status:ApprovalStatus = Field(..., description="同意，拒绝操作")    
