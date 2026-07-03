from pydantic import BaseModel, Field
from app.common.enums import CollaborateResourceType
from datetime import datetime


class BaseResourceAccess(BaseModel):
    target_id: str = Field(..., description="目标ID")
    target_type: CollaborateResourceType = Field(..., description="目标类型")


class ResourceAccessCreate(BaseResourceAccess):
    password: str = Field(..., description="密码")


class ResourceAccessUpdate(BaseModel):
    password: str = Field(..., description="密码")


class ResourceAccessResponse(BaseResourceAccess):
    id: str = Field(..., description="ID")
    password: str = Field(..., description="密码")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
