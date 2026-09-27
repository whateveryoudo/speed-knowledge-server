from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.space_service import SpaceService
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse
from app.schemas.space_member import SpaceMemberCreate
from app.core.deps import get_db, get_current_user, get_space_by_host
from app.services.space_member_service import SpaceMemberService
from app.models.user import User
from app.models.space import Space
from app.common.enums import SpaceType

router = APIRouter()


@router.post("/member", response_model=SpaceResponse)
def add_member(member: SpaceMemberCreate, db: Session = Depends(get_db)):
    return SpaceMemberService(db).add_member(member)


@router.post("/", response_model=SpaceResponse)
def create_space(
    space_create: SpaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SpaceService(db).create_space(space_create=space_create, owner_id=user.id)


@router.get("/list", response_model=list[SpaceResponse])
def list_my_spaces(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return SpaceService(db).list_spaces_by_user_id(user.id)


@router.get("/by_domain/{space_domain}", response_model=SpaceResponse)
def get_space_by_domain(space_domain: str, db: Session = Depends(get_db)):
    """根据域名获取空间（子域名访问）"""
    row = SpaceService(db).get_space_by_domain(space_domain)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在")
    return row


@router.get("/current/access", response_model=SpaceResponse)
def space_access(
    space: Space = Depends(get_space_by_host),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """校验当前用户是否可以访问该空间（前端layout使用）"""
    if space.type == SpaceType.ORGANIZATION.value:
        is_member = SpaceMemberService(db).check_member(
            space_id=space.id, user_id=current_user.id
        )
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="你不是该空间成员，可联系空间管理员添加",
            )
    return space


@router.get("/", response_model=SpaceResponse | None)
def get_my_space(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    space = SpaceService(db).get_my_space(user.id)
    if space is None:
        return None
    return space


@router.put("/{space_domain}", response_model=SpaceUpdate)
def update_space(space_domain: str, space: SpaceUpdate, db: Session = Depends(get_db)):
    return SpaceService(db).update_space(space)


@router.get("/check-domain-available", response_model=bool)
def check_domain_available(domain: str, db: Session = Depends(get_db)) -> bool:
    if not SpaceService(db).check_domain_avaliable(domain):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="域名已被使用"
        )
    return True
