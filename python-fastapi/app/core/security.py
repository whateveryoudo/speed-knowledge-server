"""安全相关"""

def verify_password(plain_password: str, hased_password: str) -> bool:
    """密码校验

    Args:
        plain_password (str): 未加密码
        hased_password (str): hash后的密码（数据库）

    Returns:
        bool: 是否正确
    """
    return False

def get_password_hash(plain_passord: str) -> str:
    """密码hash处理"""
    return plain_passord    