from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.schemas.team_member import TeamMemberCreate, TeamMemberResponse
from app.services.team_member_service import TeamMemberService
from app.core.deps import get_db
from typing import List
from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/list", response_model=List[TeamResponse])
def get_team_list(space_id: str, db: Session = Depends(get_db)):
    return TeamService(db).get_team_list_by_space_id(space_id)


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


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: str, db: Session = Depends(get_db)):
    return TeamService(db).get_team(team_id)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team: TeamUpdate, db: Session = Depends(get_db)):
    return TeamService(db).update_team(team)
