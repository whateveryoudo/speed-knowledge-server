from enum import Enum

class PermissionScopeType(str, Enum):
    """权限作用域类型"""

    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档
    SPACE = "space"  # 空间
    TEAM = "team"  # 团队
