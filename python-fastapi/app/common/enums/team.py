"""枚举类"""

from enum import Enum


class TeamVisibility(str, Enum):
    """团队可见性"""

    PUBLIC = "public"  # 公开
    PRIVATE = "private"  # 私有


class TeamMemberRole(str, Enum):
    """团队成员角色"""

    OWNER = "owner"  # 所有者(团队创建者，拥有所有权限)
    ADMIN = "admin"  # 管理员(拥有管理权限,不能删除团队)
    MEMBER = "member"  # 成员(有限的权限)
    EXTERNAL = "external"  # 外部成员（只能查看自己所在的团队知识库文档）
