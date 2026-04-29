from enum import Enum


class NotificationListType(str, Enum):
    MENTION_OR_COMMENT = "mention_or_comment"
    LIKE = "like"
    MENTION = "mention"
    FOLLOW = "follow"
    TODO = "todo"
    SYSTEM = "system"
    OTHER = "other"


class NotificationBizType(str, Enum):
    MENTION = "mention"
    COMMENT = "comment"
    LIKE = "like"
    # 细化一些协作的场景
    FOLLOW = "follow"
    SYSTEM = "system"
    JOIN_COLLABORATOR = "join_collaborator"
    APPLY_COLLABORATOR = "apply_collaborator"
