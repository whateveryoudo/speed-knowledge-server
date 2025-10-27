"""安全相关工具库"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password:str) -> str:
    """密码hash"""
    return pwd_context.hash(password)