from pydantic import BaseModel, Field
from app.common.enums.space import SpaceMemberRole


class SpaceMemberCreate(BaseModel):
    space_id: str = Field(..., description="空间ID")
    user_id: int = Field(..., description="用户ID")
    role: SpaceMemberRole = Field(..., description="角色")


class SpaceMemberUpdate(BaseModel):
    space_id: str = Field(..., description="空间ID")
    user_id: int = Field(..., description="用户ID")
    role: SpaceMemberRole = Field(..., description="角色")
