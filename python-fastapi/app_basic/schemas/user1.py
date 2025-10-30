"""用户数据模式"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """创建用户模式"""

    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """更新用户模式"""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    """用户响应模式"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模式"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模式"""

    user_id: Optional[int] = None

