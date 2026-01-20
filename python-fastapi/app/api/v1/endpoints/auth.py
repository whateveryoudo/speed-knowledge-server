from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import random
import string
import io
import uuid
import redis
import base64
from app.common.simpleImageCaptcha import SimpleImageCaptcha
from fastapi.responses import StreamingResponse
from app.core.redis_client import get_redis
from app.schemas.user import Token, CaptchaResponse
from app.core.deps import get_db
from app.services.user_service import UserService
from app.core.security import create_access_token, verify_captcha
from app.schemas.user import OAuth2PasswordRequestFormWithCaptcha

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestFormWithCaptcha = Depends(),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    print(form_data)
    """用户登录（支持邮箱或用户名登录）"""
    if verify_captcha(
        captcha_id=form_data.verificateId,
        captcha_value=form_data.verificateCode,
        client_ip=request.client.host,
        redis_client=redis_client,
    ):
        """验证码校验通过"""
        user_service = UserService(db)
        # form_data.username 可以是邮箱或用户名
        user = user_service.authenticate(form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名/邮箱或密码错误",
                headers={"WWW-Authenticate", "Bearer"},
            )
        print(user.id)
        access_token = create_access_token(data={"sub": str(user.id)})
        print(access_token)
        return {"access_token": access_token, "token_type": "bearer"}


@router.get("/getVerificateCode", response_model=CaptchaResponse)
async def getverificate_code(
    request: Request, redis_client: redis.Redis = Depends(get_redis)
) -> CaptchaResponse:
    """获取图形验证码"""
    client_ip = request.client.host
    # 是否有代理
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    # 生成4位随机验证码
    captcha_txt = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    image = SimpleImageCaptcha(width=90, height=32, font_sizes=(25, 28))

    data_stream = image.generate(captcha_txt)

    captcha_id = str(uuid.uuid4())

    # 将验证码信息存入Redis（5分钟过期）
    captcha_key = f"captcha_{captcha_id}"
    captcha_ip_key = f"captcha_ip_{captcha_id}"
    print(f"captcha_txt的值是{captcha_txt.lower()}")
    redis_client.setex(name=captcha_key, time=300, value=captcha_txt.lower())
    # 存储绑定关系
    redis_client.setex(name=captcha_ip_key, time=300, value=client_ip)
    print(f"[验证码] ID:{captcha_id},文本: {captcha_txt}")

    # 返回流信息
    image_bytes = data_stream.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return CaptchaResponse(
        captcha_id=captcha_id, captcha_image=f"data:image/png;base64,{image_base64}"
    )

    # return StreamingResponse(
    #     io.BytesIO(data_stream.getvalue()),
    #     media_type="image/png",
    #     headers={
    #         "capcha-key": "some-unique-id"
    #     }
    # )
