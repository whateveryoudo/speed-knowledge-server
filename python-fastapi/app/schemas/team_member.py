from pydantic import BaseModel, Field
from app.common.enums.team import TeamMemberRole
from datetime import datetime
from typing import Optional
class TeamMemberBase(BaseModel):
    team_id: str = Field(..., description="所属团队ID")
    user_id: int = Field(..., description="用户ID")
    role: TeamMemberRole = Field(..., description="角色")
    # join_at: Optional[datetime] = Field(default_factory=datetime.now, description="加入时间")

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(TeamMemberBase):
    role: Optional[TeamMemberRole] = Field(None, description="角色")
    join_at: Optional[datetime] = Field(None, description="加入时间")

class TeamMemberResponse(TeamMemberBase):
    id: str = Field(..., description="团队成员ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        from_attributes = True