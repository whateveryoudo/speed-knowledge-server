from pydantic import BaseModel, Field
from app.common.enums.team import TeamVisibility
from typing import Optional, List
from datetime import datetime


class TeamBase(BaseModel):
    name:str = Field(..., min_length=2, max_length=30, description="团队名称")
    description: Optional[str] = Field(None, description="团队简介")
    icon: Optional[str] = Field(None, description="团队图标")
    visibility: TeamVisibility = Field(..., description="团队可见性")
    owner_id: int = Field(..., description="团队所有者ID")
    space_id: str = Field(..., description="所属空间ID")
    slug: str = Field(..., description="团队标识")


class TeamCreate(TeamBase):
    members: Optional[List[int]] = Field(None, description="团队成员ID列表")
    pass


class TeamUpdate(TeamBase):
    name: Optional[str] = Field(
        None, min_length=2, max_length=30, description="团队名称"
    )
    icon: Optional[str] = Field(None, description="团队图标")
    description: Optional[str] = Field(None, description="团队简介")


class TeamResponse(TeamBase):
    id: str = Field(..., description="团队ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
