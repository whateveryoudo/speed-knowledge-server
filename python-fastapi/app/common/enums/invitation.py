from enum import Enum


class InvitationStatus(str, Enum):
    """邀请链接状态"""

    ACTIVE = "active"  # 正常
    REVOKED = "revoked"  # 已撤销
