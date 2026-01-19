from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.team_service import TeamService
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.schemas.team_member import TeamMemberCreate, TeamMemberResponse
from app.services.team_member_service import TeamMemberService
from app.core.deps import get_db

router = APIRouter()


@router.post("/member", response_model=TeamMemberResponse)
def add_member(member: TeamMemberCreate, db: Session = Depends(get_db)):
    return TeamMemberService(db).add_member(member)


@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    return TeamService(db).create_team(team)


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: str, db: Session = Depends(get_db)):
    return TeamService(db).get_team(team_id)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team: TeamUpdate, db: Session = Depends(get_db)):
    return TeamService(db).update_team(team)
