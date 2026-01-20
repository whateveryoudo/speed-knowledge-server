from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.space_service import SpaceService
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse
from app.schemas.space_member import SpaceMemberCreate
from app.core.deps import get_db, get_current_user
from app.services.space_member_service import SpaceMemberService
from app.models.user import User

router = APIRouter()


@router.post("/member", response_model=SpaceResponse)
def add_member(member: SpaceMemberCreate, db: Session = Depends(get_db)):
    return SpaceMemberService(db).add_member(member)


@router.post("/", response_model=SpaceCreate)
def create_space(space: SpaceCreate, db: Session = Depends(get_db)):
    return SpaceService(db).create_space(space)

@router.get("/by_domin/{space_domin}", response_model=SpaceResponse)
def get_space(
    space_domin: str,
    db: Session = Depends(get_db),
):
    """根据域名获取空间(这里不会走权限检查)"""
    return SpaceService(db).get_space_by_domin(space_domin)

@router.get("/", response_model=SpaceResponse)
def get_space_(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SpaceService(db).get_space_by_user_id(user.id)



@router.put("/{space_domin}", response_model=SpaceUpdate)
def update_space(space_domin: str, space: SpaceUpdate, db: Session = Depends(get_db)):
    return SpaceService(db).update_space(space_domin, space)


@router.get("/check-domin-available", response_model=bool)
def check_domin_available(domin: str, db: Session = Depends(get_db)) -> bool:
    row = SpaceService(db).check_domin_available(domin)
    if row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="域名已被使用"
        )
    else:
        return True
