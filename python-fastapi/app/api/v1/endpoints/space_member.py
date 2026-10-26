from app.schemas.space_member import (
    SpaceMemberQuery,
    SpaceMemberAdd,
    SpaceMemberAdjustDepartments,
    SpaceMemberRoleUpdate,
    SpaceMemberBatchDelete,
)

from app.services.space_member_service import SpaceMemberService
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.space import Space
from app.models.space_member import SpaceMember
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_space, require_space_admin
from app.models.user import User
from app.core.deps import get_current_user
from app.common.enums import SpaceMemberRole

router = APIRouter()


@router.get("/")
def list_space_members(
    query_in: SpaceMemberQuery = Depends(),
    db: Session = Depends(get_db),
    space: Space = Depends(get_current_space),
    user: User = Depends(get_current_user),
):
    space_member_service = SpaceMemberService(db)
    # 权限拦截
    space_member_service.ensure_member_role(
        space_id=space.id,
        user_id=user.id,
        allow_roles=None
    )
    if query_in.tab in ("resigned", "external"):
        space_member_service.ensure_member_role(
            space_id=space.id,
            user_id=user.id,
            allow_roles=[SpaceMemberRole.ADMIN, SpaceMemberRole.OWNER],
            detail_message="你无权查看外部联系人或已离职人员名单",
        )
    return space_member_service.list_members(space_id=space.id, query_in=query_in)


@router.post("/")
def add_space_member(
    data: SpaceMemberAdd,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    return SpaceMemberService(db).add_or_restore_member(space_id=space.id, data=data)


@router.post("/{member_id}/resigned")
def operate_member_resigned(
    member_id: str,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    return SpaceMemberService(db).operate_resigned(
        space_id=space.id, member_id=member_id
    )


@router.post("/batch-delete")
def batch_delete_resigned_members(
    data: SpaceMemberBatchDelete,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    return SpaceMemberService(db).batch_hard_delete_resigned(
        space_id=space.id, member_ids=data.member_ids
    )


@router.put("/{member_id}/role")
def operate_member_role(
    member_id: str,
    data: SpaceMemberRoleUpdate,
    space: Space = Depends(get_current_space),
    admin_member: SpaceMember = Depends(require_space_admin),
    db: Session = Depends(get_db),
):
    return SpaceMemberService(db).update_role(
        space_id=space.id, member_id=member_id, new_role=data.role
    )


@router.put("/{member_id}/departments")
def operate_member_departments(
    member_id: str,
    data: SpaceMemberAdjustDepartments,
    admin_member: SpaceMember = Depends(require_space_admin),
    space: Space = Depends(get_current_space),
    db: Session = Depends(get_db),
):
    return SpaceMemberService(db).adjust_departments(
        space_id=space.id, member_id=member_id, department_ids=data.department_ids
    )
