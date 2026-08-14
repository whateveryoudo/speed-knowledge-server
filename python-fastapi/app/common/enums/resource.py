from enum import Enum


class ResourceType(str, Enum):
    """资源类型"""

    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档


class ResourceRole(str, Enum):
    """资源角色"""

    READ = "read"  # 只读
    EDIT = "edit"  # 可编辑
    ADMIN = "admin"  # 管理员
    NONE = "none"  # 无权限


# 角色名称映射
resource_role_name = {
    ResourceRole.READ.value: "只读",
    ResourceRole.EDIT.value: "编辑",
    ResourceRole.ADMIN.value: "管理员",
    ResourceRole.NONE.value: "无权限",
}
