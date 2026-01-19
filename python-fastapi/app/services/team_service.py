from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from datetime import datetime
import secrets
import string

alphabet = string.ascii_letters + string.digits


class TeamService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Team)

    def _generate_slug(self) -> str:
        """生成团队短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def get_team(self, team_id: str):
        return self.get_active_query().filter(Team.id == team_id).first()

    def create_team(self, team_create: TeamCreate):
        # 排除members
        print(team_create)
        temp_slug = self._generate_slug()
        while self.get_active_query().filter(Team.slug == temp_slug).first():
            temp_slug = self._generate_slug()
        team_row = Team(**team_create.model_dump(exclude={"members"}), slug = temp_slug)
        self.db.add(team_row)
        self.db.flush()
        self.db.commit()
        self.db.refresh(team_row)
        return team_row

    def update_team(self, team_update: TeamUpdate):
        self.db.query(Team).filter(Team.id == team_update.id).update(
            team_update.model_dump()
        )
        self.db.commit()
        return True

    def delete_team(self, team_id: str):
        self.db.query(Team).filter(Team.id == team_id).update(
            {"deleted_at": datetime.now()}
        )
        self.db.commit()
        return True
