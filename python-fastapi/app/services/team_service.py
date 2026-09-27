from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.knowledge import Knowledge
from app.schemas.team import TeamCreate, TeamUpdate
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.base_service import BaseService
import secrets
import string
from app.services.team_member_service import TeamMemberService
from app.schemas.team_member import TeamMemberCreate
from app.schemas.team import TeamListItemResponse, TeamResponse, TeamDetailResponse
from app.common.enums import TeamMemberRole

from sqlalchemy import func

alphabet = string.ascii_letters + string.digits


class TeamService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, Team)

    def _generate_slug(self) -> str:
        """生成团队短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def get_team_list_by_space_id(self, space_id: str):
        """根据空间ID获取团队列表"""
        return self.get_active_query().filter(Team.space_id == space_id).all()

    def get_team(self, team_id: str):
        return self.get_active_query().filter(Team.id == team_id).first()

    def get_team_by_identifier(
        self, *, identifier: str, space_id: str, user_id: int
    ) -> TeamDetailResponse:
        team = (
            self.get_active_query()
            .filter(Team.space_id == space_id, (Team.slug == identifier) | (Team.id == identifier))
            .first()
        )
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")

        member = (
            self.db.query(TeamMember.role)
            .filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id)
            .first()
        )
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="你不是该团队的成员"
            )
        member_count = (
            self.db.query(TeamMember).filter(TeamMember.team_id == team.id).count()
        )
        knowledge_count = (
            self.db.query(Knowledge).filter(Knowledge.team_id == team.id).count()
        )
        base_team = TeamResponse.model_validate(team)
        return TeamDetailResponse(
            **base_team.model_dump(),
            my_role=member.role,
            member_count=member_count,
            knowledge_count=knowledge_count,
        )

    def _slug_exists(self, slug: str):
        return self.get_all_query().filter(Team.slug == slug).first() is not None

    def create_team(self, *, team_create: TeamCreate, owner_id: int):
        # 排除members
        temp_slug = self._generate_slug()
        while self._slug_exists(temp_slug):
            temp_slug = self._generate_slug()
        team_row = Team(
            **team_create.model_dump(exclude={"members"}),
            slug=temp_slug,
            owner_id=owner_id,
        )

        self.db.add(team_row)
        self.db.flush()
        # 追加默认分组
        from app.models.knowledge_group import KnowledgeGroup
        from app.schemas.knowledge_group import DEFAULT_DISPLAY_CONFIG

        team_member_service = TeamMemberService(self.db)
        team_member_service.add_member(
            TeamMemberCreate(
                team_id=team_row.id,
                user_id=owner_id,
                role=TeamMemberRole.OWNER,
            ),
            commit=False,
        )
        default_team_group = KnowledgeGroup(
            group_name="默认分组",
            team_id=team_row.id,
            user_id=owner_id,
            is_default=True,
            display_config=DEFAULT_DISPLAY_CONFIG.model_dump(),
        )
        self.db.add(default_team_group)
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

    def update_team(self, team_update: TeamUpdate):
        self.get_active_query().filter(Team.id == team_update.id).update(
            team_update.model_dump()
        )
        self.db.commit()
        return True

    def delete_team(self, team_id: str):
        team: Team | None = self.get_active_query().filter(Team.id == team_id).first()
        if team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
        if team.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="默认团队不能删除"
            )
        team.soft_delete()
        self.db.commit()
        return True

    def get_my_teams_in_space(
        self, *, user_id: int, space_id: str
    ) -> list[TeamListItemResponse]:
        """获取当前用户在指定空间下的团队列表"""
        rows = (
            self.db.query(Team, TeamMember.role)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .filter(
                Team.space_id == space_id,
                TeamMember.user_id == user_id,
                Team.deleted_at.is_(None),
            )
            .order_by(Team.created_at.desc())
            .all()
        )

        if not rows:
            return []
        team_ids = [team.id for team, _ in rows]
        # 聚合成员数量
        member_counts = dict(
            self.db.query(TeamMember.team_id, func.count(TeamMember.id))
            .filter(TeamMember.team_id.in_(team_ids))
            .group_by(TeamMember.team_id)
            .all()
        )

        # 聚合团队下知识库数量

        knowledge_counts = dict(
            self.db.query(Knowledge.team_id, func.count(Knowledge.id))
            .filter(Knowledge.team_id.in_(team_ids), Knowledge.deleted_at.is_(None))
            .group_by(Knowledge.team_id)
            .all()
        )

        result = []
        for team, role in rows:
            base_team = TeamResponse.model_validate(team)
            result.append(
                TeamListItemResponse(
                    **base_team.model_dump(),
                    my_role=role,
                    member_count=member_counts.get(team.id, 0),
                    knowledge_count=knowledge_counts.get(team.id, 0),
                    is_joined=True,
                )
            )
        return result
