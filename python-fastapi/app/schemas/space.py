from pydantic import BaseModel, Field
from app.common.enums.space import SpaceType
from typing import Optional
from datetime import datetime


class SpaceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="空间名称")
    description: Optional[str] = Field(None, description="空间描述")
    domain: Optional[str] = Field(None, description="空间域名")
    type: SpaceType = Field(..., description="空间类型")
    owner_id: int = Field(..., description="空间所有者ID")
    contact_email: str = Field(..., description="空间联系邮箱")


class SpaceCreate(SpaceBase):
    pass


class SpaceUpdate(SpaceBase):
    name: Optional[str] = Field(
        None, min_length=2, max_length=50, description="空间名称"
    )
    domain: Optional[str] = Field(None, description="空间域名")
    type: Optional[SpaceType] = Field(None, description="空间类型")
    owner_id: Optional[int] = Field(None, description="空间所有者ID")
    contact_email: Optional[str] = Field(None, description="空间联系邮箱")


class SpaceResponse(SpaceBase):
    id: str = Field(..., description="空间ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
