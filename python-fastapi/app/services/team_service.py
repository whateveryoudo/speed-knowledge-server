from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.base_service import BaseService
import secrets
import string
from app.services.team_member_service import TeamMemberService
from app.schemas.team_member import TeamMemberCreate
from app.common.enums import TeamMemberRole

alphabet = string.ascii_letters + string.digits


class TeamService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Team)

    def _generate_slug(self) -> str:
        """生成团队短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def get_team_list_by_space_id(self, space_id: str):
        """根据空间ID获取团队列表"""
        return self.get_active_query().filter(Team.space_id == space_id)

    def get_team(self, team_id: str):
        return self.get_active_query().filter(Team.id == team_id).first()

    def _slug_exists(self, slug: str):
        return self.get_all_query().filter(Team.slug == slug).first() is not None

    def create_team(self, team_create: TeamCreate):
        # 排除members
        temp_slug = self._generate_slug()
        while self._slug_exists(temp_slug):
            temp_slug = self._generate_slug()
        team_row = Team(**team_create.model_dump(exclude={"members"}), slug=temp_slug)
        self.db.add(team_row)
        self.db.flush()
        self.db.commit()
        self.db.refresh(team_row)
        return team_row

    def get_default_team(self, user_id: int, space_id: str):
        return (
            self.get_active_query()
            .filter(
                Team.is_default == True,
                Team.owner_id == user_id,
                Team.space_id == space_id,
            )
            .first()
        )

    def create_default_team(self, team_create: TeamCreate):
        # 排除members
        temp_slug = self._generate_slug()
        while self._slug_exists(temp_slug):
            temp_slug = self._generate_slug()
        team_row = Team(
            **team_create.model_dump(exclude={"members", "slug"}),
            slug=temp_slug,
            is_default=True,
        )
        self.db.add(team_row)
        self.db.flush()
        # 追加默认成员
        team_member_service = TeamMemberService(self.db)
        team_member_service.add_member(
            TeamMemberCreate(
                team_id=team_row.id,
                user_id=team_row.owner_id,
                role=TeamMemberRole.OWNER,
            )
        )
        self.db.refresh(team_row)
        return team_row

    def update_team(self, team_update: TeamUpdate):
        self.get_active_query().filter(Team.id == team_update.id).update(
            team_update.model_dump()
        )
        self.db.commit()
        return True

    def delete_team(self, team_id: str):

        team: Team | None = self.get_active_query().filter(Team.id == team_id).first()
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
            )
        if team.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="默认团队不能删除"
            )
        team.soft_delete()
        self.db.commit()
        return True
