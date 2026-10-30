from enum import Enum


class InvitationStatus(str, Enum):
    """邀请链接状态"""

    ACTIVE = "active"  # 正常
    REVOKED = "revoked"  # 已撤销

class OrgType(str,Enum):
    """组织类型"""
    SPACE = "space"  # 空间
    TEAM = "team"  # 团队
    
class InvitationType(str,Enum):
    """邀请类型"""
    LINK = "link"  # 邀请链接
    DIRECT = "direct"  # 直接邀请    

class OrgInvitationUserStatus(str,Enum):
    """登录人在受邀组织中的状态"""
    JOINED = "joined"  # 已加入
    PENDING = "pending"  # 审批中
    EXTERNAL = "EXTERNAL"  # 外部联系人    
    NOT_JOINED = "not_joined" # 还未加入的普通平台人员