from app.schemas.user import UserBrief
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import OrgType, ApprovalStatus


class OrgJoinRequestItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:str = Field(..., description="")
    org_id:str = Field(..., description="")
    org_type:OrgType = Field(..., description="")
    org_name: str = Field(default=None, description="组织名称")
    applicant_user: UserBrief = Field(..., description="申请人信息")
    status:ApprovalStatus = Field(..., description="申请状态:pending-待处理，approved-已批准，rejected-已拒绝")    