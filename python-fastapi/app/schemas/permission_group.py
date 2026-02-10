"""权限组结构"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import CollaboratorRole, CollaborateResourceType, collaborator_role_name


class PermissionGroupBase(BaseModel):
    """权限组基础结构"""

    name: str = Field(..., description="权限组名称")
    role: CollaboratorRole = Field(..., description="角色")
    target_type: CollaborateResourceType = Field(..., description="目标类型")
    target_id: str = Field(..., description="目标ID")
    collaborator_id: str = Field(..., description="所属协同记录")


class PermissionGroupCreate(PermissionGroupBase):
    """创建权限组结构"""

    model_config = {"use_enum_values": True}
    pass


class PermissionGroupResponse(PermissionGroupBase):
    """权限组响应结构"""

    id: str = Field(..., description="权限组ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PermissionGroupUpdate(BaseModel):
    role: Optional[CollaboratorRole] = Field(..., description="角色")
    target_type: Optional[CollaborateResourceType] = Field(..., description="目标类型")
    target_id: Optional[str] = Field(..., description="目标ID")
