from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Form
from typing import Union, Annotated


class OAuth2PasswordRequestFormWithCaptcha(OAuth2PasswordRequestForm):
    """扩展auth2类，携带验证码

    Args:
        OAuth2PasswordRequestForm (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        *,
        grant_type: Annotated[Union[str, None], Form(patter="password")] = None,
        username: Annotated[str, Form(..., description="用户名")],
        password: Annotated[str, Form(..., description="密码")],
        verificateId: Annotated[str, Form(..., description="验证码ID")],
        verificateCode: Annotated[str, Form(..., description="验证码")],
    ):
        super().__init__(grant_type=grant_type,username=username,password=password)
        self.verificateId = verificateId
        self.verificateCode = verificateCode


class Token(BaseModel):
    """令牌结构"""

    access_token: str
    token_type: str = "bearer"


# 图形验证码响应结构
class CaptchaResponse(BaseModel):
    """图形验证码响应体

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    captcha_id: str = Field(..., description="验证码ID，用于校验")
    captcha_image: str = Field(..., description="图片base64")


class UserBase(BaseModel):
    """用户基础类"""

    email: str
    username: str = Field(
        ..., min_length=3, max_length=50, description="用户名，用于登录"
    )
    nickname: Optional[str] = Field(None, max_length=100, description="昵称，可选")


class UserResponse(UserBase):
    """用户响应体

    Args:
        UserBase (_type_): 用户基础类
    """

    id: int
    created_at: datetime
    updated_at: datetime

    # 这里需要将响应结构orm->dict
    # v1写法
    # class Config:
    # from_attributes=True

    model_config = ConfigDict(from_attributes=True)

    # 将 UTC 时间在输出为 JSON 时转换为上海时区字符串
    # @field_serializer("created_at", "updated_at", when_used="json")
    # def _serialize_dt_to_shanghai(self, dt: datetime):
    #     from zoneinfo import ZoneInfo

    #     if dt is None:
    #         return None
    #     # 若为 naive datetime，按 UTC 处理；然后转换为上海时区并输出 ISO8601
    #     if dt.tzinfo is None:
    #         dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    #     return dt.astimezone(ZoneInfo("Asia/Shanghai")).isoformat()


class UserCreate(UserBase):
    """用户请求体"""

    verificateCode: Optional[str] = None
    verificateId: Optional[str] = None
    password: str
