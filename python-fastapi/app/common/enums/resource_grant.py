from enum import Enum



class PrincipalType(str, Enum):
    """主体类型(授权)"""

    USER = "user"  # 用户
    SPACE_ROLE = "space_role"  # 空间角色
    TEAM_ROLE = "team_role"  # 团队角色


class PrincipalRole(str, Enum):
    NONE = "none"

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

    READONLY = "readonly"
    EXTERNAL = "external"



class GrantSource(str, Enum):
    CREATOR = "creator"  # 创建者默认授权
    DEFAULT_POLICY = "default_policy"  # 团队/空间管理员默认策略
    DIRECT = "direct"  # 直接授权（手动添加)
    INVITATION = "invitation"  # 邀请
    ACCESS_REQUEST = "access_request"  # 访问请求
