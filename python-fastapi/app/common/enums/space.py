"""枚举类"""

from enum import Enum


class SpaceType(str, Enum):
    """空间类型"""

    PERSONAL = "personal"  # 个人空间
    TEAM = "team"  # 团队空间


class SpaceMemberRole(str, Enum):
    """空间成员角色"""

    OWNER = "owner"  # 所有者(空间创建者，拥有所有权限)
    ADMIN = "admin"  # 管理员(拥有管理权限,不能删除空间)
    MEMBER = "member"  # 成员(有限的权限)
    EXTERNAL = "external"  # 外部成员（只能查看自己所在的团队知识库文档）
