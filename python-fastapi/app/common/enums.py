"""枚举类"""
from enum import Enum


# ==================== 知识库分组相关枚举 ====================

class KnowledgeGroupType(str, Enum):
    """知识库布局模式"""
    CARD = "card"  # 卡片布局
    LIST = "list"  # 列表布局


class KnowledgeGroupStyle(str, Enum):
    """知识库卡片样式"""
    SIMPLE = "simple"  # 简洁
    BASIC = "basic"  # 基础
    DETAIL = "detail"  # 详情
    IMAGE = "image"  # 图片

class DocumentType(str, Enum):
    """文档类型:目前仅支持word"""
    WORD = "word"  # Word

class DocumentNodeType(str, Enum):
    """文档节点类型"""
    TITLE = "TITLE"  # 目录
    DOC = "DOC"  # 文档节点

# ==================== 知识库协同相关 ====================

class KnowledgeCollaboratorRole(int, Enum):
    """知识库协同权限"""
    READ = 1  # 只读(浏览文档 & 评论文档)
    EDIT = 2  # 编辑
    ADMIN = 3  # 管理员

class KnowledgeCollaboratorStatus(int, Enum):
    """知识库协作者状态"""
    PENDING = 1  # 申请加入中

class KnowledgeCollaboratorSource(int, Enum):
    """知识库协作者来源"""
    INVITATION = 1  # 邀请链接加入
    SEARCH_JOIN = 2  # 搜索加入

class KnowledgeInvitationStatus(int, Enum):
    """知识库邀请链接状态"""
    ACTIVE = 1  # 正常
    REVOKED = 2  # 已撤销