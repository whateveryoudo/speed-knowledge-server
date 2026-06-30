"""安全相关"""

from typing import Optional
from fastapi import HTTPException, status, Request, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta, datetime
from app.core.config import settings
from app.core.redis_client import get_redis

import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_client_ip(request: Request) -> str:
    """获取客户端 IP（nginx 等反代后优先 X-Forwarded-For）"""
    client_ip = request.client.host if request.client else ""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        client_ip = request.headers.get("X-Real-IP", client_ip).strip()
    return client_ip


def get_login_fail_count(
    redis_client: redis.Redis, client_ip: str, user_name: str
) -> int:
    """获取登录失败次数,返回最大值"""
    ip_fail_count = int(redis_client.get(name=f"login:fail:ip:{client_ip}") or 0)
    user_name_fail_count = int(
        redis_client.get(name=f"login:fail:user_name:{user_name}") or 0
    )
    return max(ip_fail_count, user_name_fail_count)


def need_login_captcha(
    redis_client: redis.Redis, client_ip: str, user_name: str
) -> bool:
    """是否需要登录验证码"""
    fail_count = get_login_fail_count(redis_client, client_ip, user_name)
    return fail_count >= settings.LOGIN_FAIL_THRESHOLD


def record_login_failure(
    redis_client: redis.Redis, client_ip: str, user_name: str
) -> None:
    """记录登录失败"""
    for key in (f"login:fail:ip:{client_ip}", f"login:fail:user_name:{user_name}"):
        count = redis_client.incr(name=key)
        if count == 1:
            redis_client.expire(name=key, time=settings.LOGIN_FAIL_WINDOW_SECONDS)


def clear_login_failure(
    redis_client: redis.Redis, client_ip: str, user_name: str
) -> None:
    """清除登录失败记录"""
    redis_client.delete(
        f"login:fail:ip:{client_ip}", f"login:fail:user_name:{user_name}"
    )


class RateLimitByIP:
    """IP限流装饰器"""

    def __init__(self, *, key_prefix: str, limit: int, window_seconds: int):
        self.key_prefix = key_prefix
        self.limit = limit
        self.window_seconds = window_seconds
        self.window_seconds = window_seconds

    def __call__(
        self, request: Request, redis_client: redis.Redis = Depends(get_redis)
    ) -> None:
        """限流检查"""
        client_ip = get_client_ip(request)
        key = f"{self.key_prefix}:{client_ip}"
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, self.window_seconds)
        if count > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="请求过于频繁"
            )


class MinIntervalByIP:
    """IP最小间隔装饰器"""

    def __init__(self, *, key_prefix: str, interval_seconds: int = 1):
        self.key_prefix = key_prefix
        self.interval_seconds = interval_seconds

    def __call__(
        self, request: Request, redis_client: redis.Redis = Depends(get_redis)
    ) -> None:
        """最小间隔检查"""
        client_ip = get_client_ip(request)
        key = f"{self.key_prefix}:{client_ip}"
        ok = redis_client.set(key, "1", nx=True, ex=self.interval_seconds)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="操作太频繁，请稍后再试",
            )


def get_password_hash(plain_passord: str) -> str:
    """密码hash处理"""
    print(plain_passord)
    return pwd_context.hash(plain_passord)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    # JWT 规范要求 sub 为字符串
    subject = to_encode.get("sub")
    if subject is not None:
        to_encode["sub"] = str(subject)

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    print(encoded_jwt)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解码访问令牌"""
    try:
        print(token)
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌"
        )


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

    redis_client.delete(captcha_key, captcha_ip_key)

    return True
