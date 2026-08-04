from enum import Enum

from google.protobuf.descriptor_pb2 import VISIBILITY_EXPORT
from app.common.enums.space import SpaceMemberRole
from app.common.enums.team import TeamMemberRole
from typing import TypeAlias, Union


class ResourceType(str, Enum):
    """资源类型"""

    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档


class PrincipalType(str, Enum):
    """主体类型(授权)"""

    USER = "user"  # 用户
    SPACE_ROLE = "space_role"  # 空间角色
    TEAM_ROLE = "team_role"  # 团队角色


class PrincipalRole(str, Enum):
    NONE = "none"

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

    READONLY = "readonly"
    EXTERNAL = "external"


class ResourceRole(str, Enum):
    """资源角色"""
    READ = "read"  # 只读
    EDIT = "edit"  # 可编辑
    ADMIN = "admin"  # 管理员
    NONE = "none"  # 无权限


class GrantSource(str, Enum):
    CREATOR = "creator"  # 创建者默认授权
    DEFAULT_POLICY = "default_policy"  # 团队/空间管理员默认策略
    DIRECT = "direct"  # 直接授权（手动设置）
    INVITATION = "invitation"  # 邀请
