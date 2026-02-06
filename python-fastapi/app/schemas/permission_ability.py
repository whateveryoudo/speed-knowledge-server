"""权限能力结构"""
from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from app.common.enums import KnowledgeAbility, DocumentAbility, CollaboratorRole,CollaborateResourceType


class PermissionAbilityBase(BaseModel):
    """权限能力基础结构"""
    permission_group_id: str = Field(..., description="权限组ID")
    enabled: bool = Field(..., description="是否启用")
    ability_key: Union[KnowledgeAbility, DocumentAbility] = Field(..., description="能力键")


class PermissionAbilityCreateByRole(BaseModel):
    """创建权限能力结构(注意:这里需要根据角色创建对应的权限能力,不是单条创建)"""
    role: CollaboratorRole = Field(..., description="角色")
    permission_group_id: str = Field(..., description="权限组ID")
    target_type: CollaborateResourceType = Field(..., description="目标类型")

class PermissionAbilityUpdate(PermissionAbilityBase):
    """更新权限能力结构"""
    enabled: Optional[bool] = Field(..., description="是否启用")
    ability_key: Optional[Union[KnowledgeAbility, DocumentAbility]] = Field(..., description="能力键")

class PermissionAbilityResponse(PermissionAbilityBase):
    """权限能力响应结构"""
    id: str = Field(..., description="权限能力ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True