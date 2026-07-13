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
from app.schemas.user import Token, CaptchaResponse, LoginErrorResponse
from app.core.deps import get_db
from app.services.user_service import UserService
from app.core.security import (
    create_access_token,
    verify_captcha,
    get_client_ip,
    MinIntervalByIP,
    RateLimitByIP,
    need_login_captcha,
    record_login_failure,
    clear_login_failure,
)

from app.schemas.user import (
    OAuth2PasswordRequestFormWithCaptcha,
    SendEmailCodeResponse,
    SendEmailCodeRequest,
)
from app.services.email_service import EmailService
from app.core.config import settings
from app.common.enums.auth import EmailScene

router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    responses={
        400: {
            "model": LoginErrorResponse,
            "description": "Bad Request",
        },
        401: {
            "model": LoginErrorResponse,
            "description": "Unauthorized",
        },
    },
)
async def login(
    request: Request,
    _: None = Depends(RateLimitByIP(key_prefix="auth", limit=10, window_seconds=60)),
    form_data: OAuth2PasswordRequestFormWithCaptcha = Depends(),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    print(form_data)

    client_ip = get_client_ip(request)
    user_name = form_data.username
    captcha_required = need_login_captcha(redis_client, client_ip, user_name)

    if captcha_required and not (form_data.verificateId and form_data.verificateCode):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "需要验证码",
                "captcha_required": True,
            },
        )

    if captcha_required:
        verify_captcha(
            captcha_id=form_data.verificateId,
            captcha_value=form_data.verificateCode,
            client_ip=get_client_ip(request),
            redis_client=redis_client,
        )

    """验证码校验通过"""
    user_service = UserService(db)
    # form_data.username 可以是邮箱或用户名
    user = user_service.authenticate(form_data.username, form_data.password)

    if not user:
        # 记录失败次数
        record_login_failure(redis_client, client_ip, user_name)
        # 判断是否需要验证码
        captcha_required = need_login_captcha(redis_client, client_ip, user_name)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "用户名/邮箱或密码错误",
                "captcha_required": captcha_required,
            },
            headers={"WWW-Authenticate", "Bearer"},
        )
    print(user.id)
    # 清除登录失败记录
    clear_login_failure(redis_client, client_ip, user_name)
    access_token = create_access_token(data={"sub": str(user.id)})
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/getVerificateCode", response_model=CaptchaResponse)
async def getverificate_code(
    request: Request,
    _: None = Depends(MinIntervalByIP(key_prefix="captcha:min_interval", interval_seconds=1)),
    __: None = Depends(
        RateLimitByIP(key_prefix="captcha:rate_limit", limit=20, window_seconds=60)
    ),
    redis_client: redis.Redis = Depends(get_redis),
) -> CaptchaResponse:
    """获取图形验证码"""
    client_ip = get_client_ip(request)
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


@router.post("/sendEmailCode", response_model=SendEmailCodeResponse)
async def send_email_code(
    body: SendEmailCodeRequest,
    _: None = Depends(MinIntervalByIP(key_prefix="email_code:min_interval", interval_seconds=1)),
    __: None = Depends(
        RateLimitByIP(key_prefix="email_code:rate_limit", limit=10, window_seconds=60)
    ),
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> SendEmailCodeResponse:
    email = body.email.lower()
    scene = body.scene

    if scene == EmailScene.REGISTER:
        # 注册场景
        user_service = UserService(db)
        user = user_service.get_by_email(email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已存在"
            )

    cooldown_key = f"email_code_cooldown:{scene}:{email}"
    if redis_client.exists(cooldown_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="发送频率过高，请稍后再试",
        )
    code = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

    code_key = f"email_code:{scene.value}:{email}"
    

    email_service = EmailService()
    email_service.send_verification_code(scene, email, code)


    redis_client.setex(
        name=code_key, time=settings.EMAIL_CODE_EXPIRE_SECONDS, value=code
    )
    redis_client.setex(
        name=cooldown_key, time=settings.EMAIL_CODE_COOLDOWN_SECONDS, value=1
    )
    return SendEmailCodeResponse(
        message="验证码已发送", expire_seconds=settings.EMAIL_CODE_EXPIRE_SECONDS
    )
