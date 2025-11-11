"""用户端点"""

from fastapi import APIRouter, Depends, status, HTTPException, Request
from app.schemas.user import UserResponse, UserCreate
from sqlalchemy.orm.session import Session
from app.core.deps import get_db
from app.models.user import User
import redis
from app.services.user_service import UserService
from app.core.security import verify_captcha
from app.core.redis_client import get_redis

router = APIRouter()


@router.post("/", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> int:
    """创建用户

    Args:
        user_in (UserCreate): 入参
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        int: 用户id
    """
    print(user_in)
    if verify_captcha(
        captcha_id=user_in.verificateId,
        captcha_value=user_in.verificateCode,
        client_ip=request.client.host,
        redis_client=redis_client,
    ):
        """验证码校验通过"""

        user_service = UserService(db)
        # 检查邮箱是否已注册
        existing_user = user_service.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已注册"
            )

        # 检查用户名是否已存在
        existing_user = user_service.get_by_username(user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该用户名已被使用"
            )

        created_user = user_service.create(user_in)

        return created_user.id
