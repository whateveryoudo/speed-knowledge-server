from fastapi import HTTPException, status
from typing import Sequence
from app.models.team_member import TeamMember
from app.schemas.team_member import TeamMemberCreate, TeamMemberResponse
from sqlalchemy.orm import Session
from app.common.enums import TeamMemberRole

from app.repositories import TeamMemberRepository

class TeamMemberService:
    """团队成员服务(这里不添加软删除)"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = TeamMemberRepository(db)

    def add_member(self, team_member_create: TeamMemberCreate, *, commit: bool = True) -> TeamMemberResponse:
        team_member_row = TeamMember(**team_member_create.model_dump())
        self.db.add(team_member_row)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(team_member_row)
        return team_member_row

    def ensure_member_role(
        self, * , team_id: str, user_id: int, 
        allow_roles: Sequence[TeamMemberRole] | TeamMemberRole | None = None
    ) -> TeamMember:
        """校验团队成员以及角色权限"""
        member = self.repo.get_by_team_and_user(team_id, user_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你不是团队成员")
        if allow_roles is not None:
            if isinstance(allow_roles, TeamMemberRole):
                roles_set = {allow_roles}
            else:
                roles_set = set(allow_roles)
            if member.role not in roles_set:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="你无权执行此操作")
        return member