from app.models.team_member import TeamMember
from app.schemas.team_member import TeamMemberCreate, TeamMemberResponse
from sqlalchemy.orm import Session


class TeamMemberService:
    """团队成员服务(这里不添加软删除)"""

    def __init__(self, db: Session):
        self.db = db

    def add_member(self, team_member_create: TeamMemberCreate) -> TeamMemberResponse:
        team_member_row = TeamMember(**team_member_create.model_dump())
        self.db.add(team_member_row)
        self.db.flush()
        self.db.commit()
        self.db.refresh(team_member_row)
        return team_member_row
