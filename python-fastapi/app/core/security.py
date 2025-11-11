"""安全相关"""

from typing import Optional
from fastapi import HTTPException, status, Request
from sqlalchemy import delete
from typing_extensions import deprecated
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta, datetime
from app.core.config import settings
import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hased_password: str) -> bool:
    """密码校验

    Args:
        plain_password (str): 未加密码
        hased_password (str): hash后的密码（数据库）

    Returns:
        bool: 是否正确
    """
    return pwd_context.verify(plain_password, hased_password)


def get_password_hash(plain_passord: str) -> str:
    """密码hash处理"""
    print(plain_passord)
    return pwd_context.hash(plain_passord)


def create_access_token(data: dict, expires_delta: Optional[timedelta]):
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow + expires_delta
    else:
        expire = datetime.utcnow + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_captcha(
    captcha_id: str, captcha_value: str, client_ip: str, redis_client: redis.Redis
):
    """图形验证码校验

    Args:
        captcha_id (str): _description_
        captcha_value (str): _description_
        client_ip (str): _description_
        redis_client (redis.Redis): _description_
    """
    captcha_key = f"captcha_{captcha_id}"
    captcha_ip_key = f"captcha_ip_{captcha_id}"

    stored_value = redis_client.getex(name=captcha_key)
    print(captcha_ip_key,stored_value)
    if not stored_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码不存在或已过期"
        )

    stored_ip = redis_client.get(name=captcha_ip_key)
    if not stored_ip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码IP绑定信息不存在"
        )

    if isinstance(stored_value, bytes):
        stored_value = stored_value.decode("utf-8")
    if isinstance(stored_ip, bytes):
        stored_ip = stored_ip.decode("utf-8")

    if stored_ip != client_ip:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="IP地址不匹配，校验失败"
        )

    if stored_value.lower() != captcha_value.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误"
        )

    # redis_client.delete(captcha_key,captcha_ip_key)

    return True
