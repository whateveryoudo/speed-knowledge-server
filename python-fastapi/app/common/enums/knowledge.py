"""枚举类"""

from enum import Enum


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


# ==================== 知识库协同相关 ====================


class KnowledgeFromWay(str, Enum):
    """知识库来源方式"""

    OWN = "own"  # 个人知识库
    COLLABORATION = "collaboration"  # 协同知识库
