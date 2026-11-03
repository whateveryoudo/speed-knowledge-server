from app.common.enums import OrgType
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.org_invitation import OrgInvitation
from typing import Optional

from app.schemas.org_invitation import OrgInvitationResponse, OrgInvitationAcceptResponse,OrgInvitationPublicInfo, OrgInvitationUpdateSettings

from app.services.org_invitation_service import OrgInvitationService
from sqlalchemy.orm import Session


router = APIRouter()


@router.post("/{org_type}/{org_id}/my-invitation")
def get_or_init_my_invitation(
    org_type:OrgType,
    org_id:str,
    data: OrgInvitationUpdateSettings,
    current_user:User=Depends(get_current_user),
    db: Session = Depends(get_db)
)->Optional[OrgInvitationResponse]:
    """管理员打开邀请弹框（获取已有的配置链接信息或初始化）"""
    invitation_service = OrgInvitationService(db)
    return invitation_service.get_my_invitation(org_type=org_type,org_id=org_id,
    data=data,
    operator_id=current_user.id)

@router.put("/{token}/update")
def save_invitation_settings(
    token:str,
    data:OrgInvitationUpdateSettings,
    current_user:User=Depends(get_current_user),
    db: Session = Depends(get_db)
)->Optional[OrgInvitationResponse]:
    """修改邀请配置"""
    invitation_service = OrgInvitationService(db)
    return invitation_service.save_and_get_invitation(token=token,data=data, operator_id=current_user.id)

@router.put("/{token}/reset")
def reset_invitation_token(
    token:str,
    current_user:User=Depends(get_current_user),
    db: Session = Depends(get_db)
)->Optional[OrgInvitationResponse]:
    """重置邀请token"""
    invitation_service = OrgInvitationService(db)
    return invitation_service.reset_token(token=token, operator_id=current_user.id)

@router.get("/info/{token}", response_model=OrgInvitationPublicInfo)
def get_invitation_public_info(
    token:str,
    current_user:User=Depends(get_current_user),
    db: Session = Depends(get_db)
)->OrgInvitationPublicInfo:
    """访问端，拿到链接后"""
    invitation_service = OrgInvitationService(db)
    return invitation_service.get_public_info(token=token, current_user_id=current_user.id)

@router.post("/accept/{token}", response_model=OrgInvitationAcceptResponse)
def accept_inviation(
    token:str,
    current_user:User=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrgInvitationAcceptResponse:
    """点击加入"""
    invitation_service = OrgInvitationService(db)
    return invitation_service.accept_invitation(token=token, user_id=current_user.id)

