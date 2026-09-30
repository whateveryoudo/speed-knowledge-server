from app.services.knowledge_group_service import KnowledgeGroupService
from app.services import team_service
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.schemas.team_member import TeamMemberCreate, TeamMemberResponse
from app.services.team_member_service import TeamMemberService
from app.services.knowledge_group_service import KnowledgeGroupService
from app.schemas.knowledge_group import KnowledgeGroupResponse
from app.core.deps import get_db
from typing import List
from app.models.user import User
from app.models.space import Space
from app.schemas.team import TeamListItemResponse, TeamDetailResponse
from app.core.deps import get_current_user, get_current_space

router = APIRouter()


@router.get(
    "/list", response_model=List[TeamListItemResponse], summary="获取当前空间下我加入的团队列表"
)
def get_team_list(
    space: Space = Depends(get_current_space),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TeamService(db).get_my_teams_in_space(user_id=user.id, space_id=space.id)


@router.post("/member", response_model=TeamMemberResponse)
def add_member(member: TeamMemberCreate, db: Session = Depends(get_db)):
    return TeamMemberService(db).add_member(member)


@router.post("/", response_model=TeamResponse)
def create_team(
    team_create: TeamCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TeamService(db).create_team(team_create=team_create, owner_id=user.id)


@router.get("/{team_identifier}", response_model=TeamDetailResponse)
def get_team(
    team_identifier: str,
    space: Space = Depends(get_current_space),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TeamService(db).get_team_by_identifier(
        identifier=team_identifier, space_id=space.id, user_id=user.id
    )


@router.get("/{slug}/knowledge-groups", response_model=list[KnowledgeGroupResponse])
def get_knowledge_groups_by_slug(
    slug: str,
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    space: Space = Depends(get_current_space),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_service = TeamService(db)
    team = team_service.get_team_by_identifier(
        identifier=slug, space_id=space.id, user_id=user.id
    )
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在")
    return KnowledgeGroupService(db).get_list_with_knowledge(
        user_id=user.id, team_id=team.id, keyword=keyword
    )


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team: TeamUpdate, db: Session = Depends(get_db)):
    return TeamService(db).update_team(team)
