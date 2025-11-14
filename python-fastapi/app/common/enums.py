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