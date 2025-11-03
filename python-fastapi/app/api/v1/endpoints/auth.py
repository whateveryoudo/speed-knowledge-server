from fastapi import APIRouter,Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import random
import string
import io
import uuid
import redis
from captcha.image import ImageCaptcha
from fastapi.responses import StreamingResponse
from app.core.redis_client import get_redis
from app.schemas.user import Token
from app.core.deps import get_db

router = APIRouter()

@router.post("/login",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db) ):
    """用户登录"""
    


@router.get("/getverificate-code")
async def getverificate_code(redis_client:redis.Redis = Depends(get_redis)):
    """
    Get verification code endpoint

    Returns:
        dict: Verification code data
    """
    # 生成4位随机验证码
    captcha_text = "".join(random.choices(string.ascii_letters + string.digits, k=4))

    # 生成存入redis的key

    catcha_id = str(uuid.uuid4())

    redis_key=f"captcha:{catcha_id}"

    print(captcha_text)
    
    redis_client.setex(name=redis_key, time = 3000, value = captcha_text.lower())

    image = ImageCaptcha(width=160, height=60)

    data_stream = image.generate(captcha_text)

    return StreamingResponse(
        io.BytesIO(data_stream.getvalue()),
        media_type="image/png",
        headers={"capcha-key": "ykx-test"},
    )
