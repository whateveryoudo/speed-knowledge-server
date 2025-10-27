"""用户数据模式"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    """创建模式"""
    password:str;

class UserUpdate(UserBase):
    email: Optional[EmailStr]
    name: Optional[str]
    password: Optional[str]

class UserResponse(UserBase):
    """用户响应模式"""
    id:int;
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

    user_id:Optional[int]= None




