"""认证端点"""
import random
import string
import io
import uuid
import redis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.redis_client import get_redis
from app.core.security import create_access_token
from app.schemas.user import Token
from app.services.user_service import UserService
from captcha.image import ImageCaptcha

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """用户登录"""
    user_service = UserService(db)
    user = user_service.authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/getverificateCode")
async def getverificate_code(redis_client: redis.Redis = Depends(get_redis)):
    """获取图形验证码"""
    # 生成4位随机验证码
    captcha_txt = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=4))

    image = ImageCaptcha(width=160, height=60)

    data_stream = image.generate(captcha_txt)

    captcha_id = str(uuid.uuid4())

    # 将验证码信息存入Redis（5分钟过期）
    redis_key = f"captcha:{captcha_id}"
    print(f"redis_key:{redis_key}")
    redis_client.setex(name=redis_key, time=300, value=captcha_txt.lower())

    print(f"[验证码] ID:{captcha_id},文本: {captcha_txt}")

    # 返回流信息

    return StreamingResponse(
        io.BytesIO(data_stream.getvalue()),
        media_type="image/png",
        headers={
            "capcha-key": "some-unique-id"
        }
    )
