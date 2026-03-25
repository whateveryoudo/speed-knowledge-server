from enum import Enum
class ChatMessageRole(str, Enum):
    """AI 消息角色"""

    USER = "user"  # 用户
    ASSISTANT = "assistant"  # 助手
    SYSTEM = "system"  # 系统
    TOOL = "tool"  # 工具


class ChatMessageType(str, Enum):
    """AI 消息类型"""

    TEXT = "text"  # 文本
    TOOL_CALL = "tool_call"  # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    ERROR = "error"  # 错误

class ChatSessionStatus(str, Enum):
    """AI 会话状态"""

    ACTIVE = "active"  # 活跃
    ARCHIVED = "archived"  # 已归档
    DELETED = "deleted"  # 已删除（这里是软删除）