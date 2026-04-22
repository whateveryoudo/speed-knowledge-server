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
    INVITE = "invite"
    FOLLOW = "follow"
    SYSTEM = "system"
