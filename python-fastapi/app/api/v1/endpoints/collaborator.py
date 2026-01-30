from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.invitation import (
    InvitationResponse,
    InvitationBase,
    InvitationValidResponse,
)
from app.schemas.collaborator import (
    CollaboratorResponse,
    CollaboratorCreate,
    CollaboratorValidParams,
    CollaboratorUpdate,
    CollaboratorAudit,
)
from app.schemas.response import BaseResponse
from app.common.enums import InvitationStatus, CollaboratorStatus, CollaboratorSource
from app.models.user import User
from app.core.deps import get_db, get_current_user
from app.models.collaborator import Collaborator
from app.services.invitation_service import InvitationService
from app.services.collaborator_service import CollaboratorService

router = APIRouter()


@router.get(
    "/{resource_type}/{resource_identifier}/invitation/token",
    response_model=InvitationResponse,
)
async def get_invitation_token(
    resource_type: str,
    resource_identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    """获取邀请链接token信息(知识库/文档)"""
    invitation_token_service = InvitationService(db)
    invitation_token_info = invitation_token_service.get_invitation_token(
        resource_type, resource_identifier
    )
    return invitation_token_info


@router.put("/invitation/token/{invitation_id}", response_model=InvitationResponse)
async def update_invitation_token(
    invitation_id: str,
    invitation_token_update: InvitationBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    """更新邀请链接token信息(权限或是否需要审核)"""
    invitation_token_service = InvitationService(db)
    invitation_token_info = invitation_token_service.update_invitation_token(
        invitation_id, invitation_token_update
    )
    return invitation_token_info


@router.put(
    "/invitation/{invitation_id}/reset",
    response_model=InvitationResponse,
)
async def reset_invitation_token(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    """重置知识库邀请链接token信息"""
    invitation_token_service = InvitationService(db)
    invitation_token_info = invitation_token_service.reset_invitation_token(
        invitation_id
    )
    return invitation_token_info


@router.get("/invitation/valid", response_model=InvitationValidResponse)
async def get_invitation_valid_info(
    invitation_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationValidResponse:
    """获取邀请链接校验信息"""
    invitation_service = InvitationService(db)
    collaborator_service = CollaboratorService(db)
    invitation_valid_info = invitation_service.get_invitation_valid_info(
        invitation_token
    )
    if (
        invitation_valid_info is None
        or invitation_valid_info.status == InvitationStatus.REVOKED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邀请链接已失效"
        )
    collaborator_valid_info = collaborator_service.get_collaborator_valid_info(
        CollaboratorValidParams(
            knowledge_id=invitation_valid_info.knowledge_id,
            user_id=current_user.id,
        )
    )
    return InvitationValidResponse(
        invitation=invitation_valid_info, collaborator=collaborator_valid_info
    )


@router.get(
    "/{resource_type}/{resource_identifier}/list",
    response_model=List[CollaboratorResponse],
)
async def get_collaborator_list(
    resource_type: str,
    resource_identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CollaboratorResponse]:
    """获取协作者列表"""
    collaborator_service = CollaboratorService(db)
    collaborators = collaborator_service.get_collaborators(
        resource_type, resource_identifier
    )
    return collaborators


@router.post("/collaborator/default/create", response_model=CollaboratorResponse)
async def create_default_collaborator(
    default_collaborator_in: CollaboratorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaboratorResponse:
    """创建默认协作者(用于测试，之前没加)"""
    collaborator_service = CollaboratorService(db)
    return collaborator_service.join_default_collaborator(
        CollaboratorCreate(
            user_id=current_user.id,
            knowledge_id=default_collaborator_in.knowledge_id,
        ),
        use_by_router=True,
    )


@router.post("/invitation/apply", response_model=CollaboratorResponse)
async def apply_invitation(
    invitation_info: CollaboratorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaboratorResponse:
    """点击申请加入知识库/文档"""
    # 先校验是否合法
    invitation_service = InvitationService(db)
    collaborator_service = CollaboratorService(db)
    invitation_valid_info = invitation_service.get_invitation_by_token(
        invitation_info.invitation_token
    )
    if (
        invitation_valid_info is None
        or invitation_valid_info.status == InvitationStatus.REVOKED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邀请链接已失效"
        )
    collaborator_valid_info = collaborator_service.get_collaborator_valid_info(
        CollaboratorValidParams(
            knowledge_id=invitation_valid_info.knowledge_id,
            user_id=current_user.id,
        )
    )
    print(invitation_valid_info)
    if collaborator_valid_info:
        if collaborator_valid_info.status == CollaboratorStatus.ACCEPTED.value:
            return BaseResponse.success_reponse(
                data=collaborator_valid_info, message="您已加入该知识库"
            )
        elif collaborator_valid_info.status == CollaboratorStatus.PENDING.value:
            return BaseResponse.success_reponse(
                data=collaborator_valid_info, message="等待管理员审核"
            )

    # 根据邀请链接的配置初始化协作者状态
    collaborator_status = (
        CollaboratorStatus.PENDING.value
        if invitation_valid_info.need_approval == 1
        else CollaboratorStatus.ACCEPTED.value
    )
    temp_collaborator_info = Collaborator(
        user_id=current_user.id,
        knowledge_id=invitation_valid_info.knowledge_id,
        status=collaborator_status,
        source=CollaboratorSource.INVITATION.value,
        role=invitation_valid_info.role,
    )
    return collaborator_service.join_collaborator(temp_collaborator_info)


@router.delete(
    "/collaborator/{collaborator_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_collaborator(
    collaborator_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """删除知识库协作者"""
    collaborator_service = CollaboratorService(db)
    collaborator_service.delete_collaborator(collaborator_id)


@router.put("/collaborator/{collaborator_id}", response_model=CollaboratorResponse)
async def update_collaborator_info(
    collaborator_id: str,
    collaborator_info: CollaboratorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CollaboratorResponse:
    """更新知识库协作者信息"""
    collaborator_service = CollaboratorService(db)
    return collaborator_service.update_collaborator_info(
        collaborator_id, collaborator_info
    )


@router.post(
    "/collaborator/{collaborator_id}/audit",
    response_model=CollaboratorResponse,
)
async def audit_collaborator(
    collaborator_id: str,
    audit_in: CollaboratorAudit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Optional[CollaboratorResponse]:
    """审核知识库协作者"""
    collaborator_service = CollaboratorService(db)
    return collaborator_service.audit_collaborator(collaborator_id, audit_in)
