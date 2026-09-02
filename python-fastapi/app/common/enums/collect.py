from enum import Enum



class CollectTargetType(str, Enum):
    """收藏目标类型"""

    KNOWLEDGE = "knowledge"  # 知识
    DOCUMENT = "document"  # 文档