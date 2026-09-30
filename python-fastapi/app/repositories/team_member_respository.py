from app.repositories import BaseRepository
from app.models.team_member import TeamMember
from sqlalchemy.orm import Session
from typing import Optional

class TeamMemberRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db, TeamMember)

    def get_by_team_and_user(self, team_id: str, user_id: int) -> Optional[TeamMember]:
        return (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
            .first()
        )
