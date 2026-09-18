from pydantic import BaseModel, Field, ConfigDict
from app.common.enums.resource import ResourceRole
from app.common.enums import PrincipalType, PrincipalRole
from typing import Optional, Literal


class CollaborationUserBrief(BaseModel):
    """协同用户简要信息"""

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")


class ResourceCollaborationQuery(BaseModel):
    """权限聚合页面：查询参数"""

    keyword: Optional[str] = Field(None, description="仅搜索用户行：用户名/昵称")
    resource_role: Optional[ResourceRole] = Field(None, description="角色")


class ResourceCollaborationItem(BaseModel):
    """权限聚合页面：角色组 | 协同用户组"""

    # role_group: 角色组
    # pending: 邀请审批中
    # user：直接用户协同者
    row_type: Literal["role_group", "pending", "user"] = Field(
        ..., description="行类型"
    )
    principal_type: PrincipalType = Field(..., description="主体类型")
    principal_id: str = Field(..., description="主体ID")
    principal_role: PrincipalRole = Field(..., description="主体角色")
    user: Optional[CollaborationUserBrief] = Field(None, description="用户信息概要")
    display_name: str = Field(..., description="显示名称(某些角色会显示成一些角色名)")
    locked: bool = Field(..., description="是否锁定(不允许切换角色)")
    resource_role: Optional[ResourceRole] = Field(None, description="角色")
    source: str = Field(..., description="来源")
    status: Literal["pending", "effective"] = Field(..., description="状态")
    can_manage: bool = Field(..., description="当前登录人能否管理这一行")
    grant_id: Optional[str] = Field(..., description="授权ID")
    access_request_id: Optional[str] = Field(..., description="访问请求ID(pending时有)")
