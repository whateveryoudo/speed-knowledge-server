"""旧协作者模块兼容枚举。

V2 权限链路已经使用 ResourceRole / ResourceType；这里暂时保留旧枚举，
用于尚未下线的 Collaborator 模型、服务和接口。
"""

from enum import Enum


class CollaboratorRole(int, Enum):
    """旧协作者角色（文档不包含管理员角色）。"""

    READ = 1
    EDIT = 2
    ADMIN = 3


collaborator_role_name = {
    CollaboratorRole.READ.value: "只读",
    CollaboratorRole.EDIT.value: "编辑",
    CollaboratorRole.ADMIN.value: "管理员",
}


class CollaboratorStatus(int, Enum):
    """旧协作者状态。"""

    PENDING = 1
    ACCEPTED = 2


class CollaboratorSource(int, Enum):
    """旧协作者来源。"""

    CREATOR = 0
    INVITATION = 1
    SEARCH_JOIN = 2


class CollaborateResourceType(str, Enum):
    """旧协作者资源类型。"""

    KNOWLEDGE = "knowledge"
    DOCUMENT = "document"
