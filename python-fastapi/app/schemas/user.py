from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime

class Token(BaseModel):
    """令牌结构"""

    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    """用户基础类"""

    email: str
    name: str = Field(..., min_length=1, max_length=100)

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
    @field_serializer("created_at", "updated_at", when_used="json")
    def _serialize_dt_to_shanghai(self, dt: datetime):
        from zoneinfo import ZoneInfo
        if dt is None:
            return None
        # 若为 naive datetime，按 UTC 处理；然后转换为上海时区并输出 ISO8601
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(ZoneInfo("Asia/Shanghai")).isoformat()

class UserCreate(UserBase):
    """用户请求体"""

    password: str

