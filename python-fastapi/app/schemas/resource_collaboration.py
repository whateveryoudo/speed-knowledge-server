from app.schemas.user import UserResponse
from pydantic import BaseModel, Field
from app.common.enums.resource import ResourceRole
from typing import Optional, Literal
from app.schemas.query import Pagination


class ResourceCollaborationItem(BaseModel):
    user: UserResponse = Field(..., description="用户信息")
    resource_role: Optional[ResourceRole] = Field(None, description="角色")
    source: str = Field(..., description="来源")
    status: Literal["pending", "effective"] = Field(..., description="状态")
    can_manage: bool = Field(..., description="是否可管理")
    access_request_id: Optional[str] = Field(..., description="访问请求ID")


class ResourceCollaborationQuery(Pagination):
    """资源协作查询"""
    pass