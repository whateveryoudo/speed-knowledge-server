"""权限组结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import PermissionScopeType


class PermissionGroupBase(BaseModel):
    """权限组基础结构"""

    name: str = Field(..., description="权限组名称")
    role_key: str = Field(..., description="作用域内的角色标识")
    scope_type: PermissionScopeType = Field(..., description="作用域类型")
    scope_id: str = Field(..., description="作用域ID")


class PermissionGroupCreate(PermissionGroupBase):
    """创建权限组结构"""
    pass


class PermissionGroupResponse(PermissionGroupBase):
    """权限组响应结构"""

    id: str = Field(..., description="权限组ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PermissionGroupUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="权限组名称"
    )
    role_key: Optional[str] = Field(
        default=None, min_length=1, max_length=30, description="作用域内的角色标识"
    )
