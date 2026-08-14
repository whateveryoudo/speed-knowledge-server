from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.resource_invitation import (
    ResourceInvitationResponse,
    ResourceInvitationJoinRequest,
    ResourceInvitationJoinResponse,
    ResourceInvitationUpdate,
    ResourceInvitationCreate,
)
from app.core.deps import get_db, get_current_user
from app.common.enums import ResourceType
from app.models.user import User
from app.services.permission_service import PermissionService
from app.services.resource_invitation_service import ResourceInvitationService

router = APIRouter()


def _assert_can_manage_resource_invitation(
    *, db: Session, user_id: int, resource_type: ResourceType, resource_id: str
):
    """校验用户是否有权管理资源邀请配置。"""
    PermissionService(db).assert_can_manage_access_setting(
        user_id, resource_type, resource_id
    )


@router.post("/join", response_model=ResourceInvitationJoinResponse)
async def join_by_invitation(
    join_in: ResourceInvitationJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationJoinResponse:
    """通过邀请链接访问资源或提交访问申请"""
    service = ResourceInvitationService(db)
    try:
        result = service.join_by_invitation(
            token=join_in.token,
            applicant_user_id=current_user.id,
            apply_message=join_in.apply_message,
            submit_request=join_in.submit_request,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.get(
    "/resource/{resource_type}/{resource_id}", response_model=ResourceInvitationResponse
)
async def get_invitation_by_resource(
    resource_type: ResourceType,
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationResponse:
    """获取资源的邀请配置"""
    _assert_can_manage_resource_invitation(
        db=db,
        user_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    invitation = ResourceInvitationService(db).get_by_resource(
        resource_type=resource_type, resource_id=resource_id
    )
    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="该资源尚未创建邀请链接"
        )

    return invitation


@router.post("", response_model=ResourceInvitationResponse)
def create_or_update_invitation(
    invitation_in: ResourceInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationResponse:
    """创建或更新邀请配置"""
    _assert_can_manage_resource_invitation(
        db=db,
        user_id=current_user.id,
        resource_type=invitation_in.resource_type,
        resource_id=invitation_in.resource_id,
    )
    service = ResourceInvitationService(db)
    try:
        invitation = service.create_or_update(
            invitation_in=invitation_in,
            inviter_id=current_user.id,
        )
        db.commit()
        db.refresh(invitation)
        return invitation
    except Exception:
        db.rollback()
        raise


@router.patch("/{invitation_id}", response_model=ResourceInvitationResponse)
def update_invitation(
    invitation_id: str,
    invitation_in: ResourceInvitationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationResponse:
    """更新邀请配置(这里仅是局部更新，采用patch)"""
    service = ResourceInvitationService(db)
    exsiting_invitation = service.get_by_id_or_404(invitation_id)
    resource_type = ResourceType(exsiting_invitation.resource_type)
    _assert_can_manage_resource_invitation(
        db=db,
        user_id=current_user.id,
        resource_type=resource_type,
        resource_id=exsiting_invitation.resource_id,
    )
    try:
        invitation = service.update(
            invitation_id=invitation_id,
            invitation_update=invitation_in,
            operator_id=current_user.id,
        )
        db.commit()
        db.refresh(invitation)
        return invitation
    except Exception:
        db.rollback()
        raise


@router.post(
    "/{invitation_id}/reset-token",
    response_model=ResourceInvitationResponse,
    status_code=status.HTTP_200_OK,
)
def reset_resource_invitation_token(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationResponse:
    """重置邀请链接"""
    service = ResourceInvitationService(db)
    invitation = service.get_by_id_or_404(invitation_id)
    resource_type = ResourceType(invitation.resource_type)
    _assert_can_manage_resource_invitation(
        db=db,
        user_id=current_user.id,
        resource_type=resource_type,
        resource_id=invitation.resource_id,
    )
    try:
        invitation = service.reset_token(
            invitation_id=invitation_id, operator_id=current_user.id
        )
        db.commit()
        db.refresh(invitation)
        return invitation
    except Exception:
        db.rollback()
        raise


@router.post(
    "/{invitation_id}/revoke",
    response_model=ResourceInvitationResponse,
    status_code=status.HTTP_200_OK,
)
def revoke_resource_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResourceInvitationResponse:
    """撤销邀请"""
    service = ResourceInvitationService(db)
    invitation = service.get_by_id_or_404(invitation_id)
    resource_type = ResourceType(invitation.resource_type)
    _assert_can_manage_resource_invitation(
        db=db,
        user_id=current_user.id,
        resource_type=resource_type,
        resource_id=invitation.resource_id,
    )
    try:
        invitation = service.revoke(
            invitation_id=invitation_id, operator_id=current_user.id
        )
        db.commit()
        db.refresh(invitation)
        return invitation
    except Exception:
        db.rollback()
        raise
