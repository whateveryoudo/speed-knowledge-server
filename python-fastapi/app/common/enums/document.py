"""枚举类"""

from enum import Enum


class DocumentHistoryType(str, Enum):
    """文档历史类型"""

    VIEW = "view"  # 浏览
    EDIT = "edit"  # 编辑
    LIKE = "like"  # 点赞
    COLLECT = "collect"  # 收藏


class DocumentType(str, Enum):
    """文档类型:目前仅支持word"""

    WORD = "word"  # Word


class DocumentNodeDragAction(str, Enum):
    """文档节点拖拽动作"""

    MOVE_AFTER = "moveAfter"  # 移动到目标节点后
    MOVE_BEFORE = "moveBefore"  # 移动到目标节点前
    PREPEND_CHILD = "prependChild"  # 插入到目标节点前


class DocumentNodeType(str, Enum):
    """文档节点类型"""

    TITLE = "TITLE"  # 目录
    DOC = "DOC"  # 文档节点
