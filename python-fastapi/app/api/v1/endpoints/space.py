from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.space_service import SpaceService
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse
from app.schemas.space_member import SpaceMemberCreate
from app.core.deps import get_db
from app.services.space_member_service import SpaceMemberService

router = APIRouter()


@router.post("/member", response_model=SpaceResponse)
def add_member(member: SpaceMemberCreate, db: Session = Depends(get_db)):
    return SpaceMemberService(db).add_member(member)

@router.post("/", response_model=SpaceCreate)
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    return SpaceService(db).create_space(space)


@router.get("/{space_id}", response_model=SpaceCreate)
def get_space(space_id: str, db: Session = Depends(get_db)):
    return SpaceService(db).get_space(space_id)


@router.put("/{space_id}", response_model=SpaceUpdate)
def update_space(space_id: str, space: SpaceUpdate, db: Session = Depends(get_db)):
    return SpaceService(db).update_space(space_id, space)


@router.get("/check-domin-available", response_model=bool)
def check_domin_available(domin: str, db: Session = Depends(get_db)) -> bool:
    row = SpaceService(db).check_domin_available(domin)
    if row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="域名已被使用"
        )
    else:
        return True
