from enum import Enum
class NotificationBizType(str, Enum):
    MENTION = "mention"
    INVITE = "invite"
    