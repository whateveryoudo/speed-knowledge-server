"""枚举类"""
from enum import Enum


# ==================== 知识库分组相关枚举 ====================

class KnowledgeIndexPageLayout(str, Enum):
    """知识库文档树首页视图"""
    CATALOG = "catalog"  # 目录视图
    CARD = "card"  # 卡片视图
    COLUMN = "column"  # 专栏视图

class KnowledgeIndexPageSort(str, Enum):
    """知识库文档树首页排序"""
    CATALOG = "catalog"  # 目录排序
    CREATE_TIME = "create_time"  # 创建时间
    UPDATE_TIME = "update_time"  # 更新时间
    LIKE_COUNT = "like_count"  # 点赞次数

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

class DocumentHistoryType(str, Enum):
    """文档历史类型"""
    VIEW = "view"  # 浏览
    EDIT = "edit"  # 编辑
    LIKE = "like"  # 点赞
    COLLECT = "collect"  # 收藏

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
    ACCEPTED = 2  # 已加入    

class KnowledgeCollaboratorSource(int, Enum):
    """知识库协作者来源"""
    CREATOR = 0  # 创建者
    INVITATION = 1  # 邀请链接加入
    SEARCH_JOIN = 2  # 搜索加入

class KnowledgeInvitationStatus(int, Enum):
    """知识库邀请链接状态"""
    ACTIVE = 1  # 正常
    REVOKED = 2  # 已撤销

class CollectResourceType(str, Enum):
    """收藏资源类型"""
    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档