from enum import Enum
class EmailScene(str, Enum):
    """AI 消息角色"""

    REGISTER = "register"  # 注册
    FORGOT_PASSWORD = "forgot_password"  # 忘记密码
    RESET_PASSWORD = "reset_password"  # 重置密码
    CHANGE_EMAIL = "change_email"  # 修改邮箱
