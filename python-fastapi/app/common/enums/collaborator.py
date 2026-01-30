"""协同相关枚举定义"""

from enum import Enum

# ==================== 协同相关枚举定义 ====================


class CollaboratorRole(int, Enum):
    """协同权限（文档不包含管理员角色）"""

    READ = 1  # 只读(浏览文档 & 评论文档)
    EDIT = 2  # 编辑
    ADMIN = 3  # 管理员


class CollaboratorStatus(int, Enum):
    """协作者状态"""

    PENDING = 1  # 申请加入中
    ACCEPTED = 2  # 已加入


class CollaboratorSource(int, Enum):
    """协作者来源"""

    CREATOR = 0  # 创建者
    INVITATION = 1  # 邀请链接加入
    SEARCH_JOIN = 2  # 搜索加入


class InvitationStatus(int, Enum):
    """邀请链接状态"""

    ACTIVE = 1  # 正常
    REVOKED = 2  # 已撤销


class CollaborateResourceType(str, Enum):
    """资源类型"""

    KNOWLEDGE = 'knowledge'  # 知识库
    DOCUMENT = 'document'  # 文档
