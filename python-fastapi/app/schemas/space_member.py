from app.schemas.query import BasePaginationQuery
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums.space import SpaceMemberRole
from app.schemas.user import UserBrief
from datetime import datetime
from app.schemas.response import PaginationResponse
from typing import Optional


class SpaceMemberQuery(BasePaginationQuery):
    tab: str = Field(default="member", description="member/external/resigned")
    keyword: str | None = Field(None, description="关键字")
    department_id: str | None = Field(None, description="部门ID")
    is_direct: bool = Field(default=False, description="是否只显示直属部门成员")


class SpaceMemberBatchDelete(BaseModel):
    member_ids: list[str] = Field(..., description="成员ID列表")


class SpaceMemberItemResponse(BaseModel):
    id: str = Field(..., description="ID")
    role: SpaceMemberRole = Field(..., description="角色")
    user: UserBrief = Field(..., description="用户信息概要")
    created_at: datetime = Field(..., description="创建时间")
    deleted_at: datetime | None = Field(None, description="离职时间")
    department_names: list[str] = Field(default_factory=list, description="部门名称列表")

    model_config = ConfigDict(from_attributes=True)


class SpaceMemberAdd(BaseModel):
    user_id: int = Field(..., description="用户ID")
    department_ids: list[str] = Field(default_factory=list, description="归属部门ID列表")
    role: SpaceMemberRole = Field(..., description="角色")


class SpaceMemberRoleUpdate(BaseModel):
    role: SpaceMemberRole = Field(..., description="角色")


class SpaceMemberBatchDelete(BaseModel):
    member_ids: list[str] = Field(..., description="成员ID列表")


class SpaceMemberAdjustDepartments(BaseModel):
    department_ids: list[str] = Field(..., description="调整的目标部门id集合")


class SpaceMemberExtra(BaseModel):
    active_member_count: int = Field(..., description="在职成员数（不包含待审批的）")


class SpaceMemberListResponse(PaginationResponse[SpaceMemberItemResponse]):
    extra: Optional[SpaceMemberExtra] = Field(
        default=None, description="一些额外附加属性（你可以自定义字段）"
    )
