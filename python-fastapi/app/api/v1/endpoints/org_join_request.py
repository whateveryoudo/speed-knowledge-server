"""组织审批记录路由"""

from fastapi import APIRouter, Depends
from app.models.user import User
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.org_join_request import (
    OrgJoinRequestAudit
)
from app.core.deps import get_current_user, get_db
from app.services.org_join_request_service import OrgJoinRequestService


router = APIRouter()


@router.post("/{request_id}/audit")
def audit_org_join_request(
    request_id: str,
    audit_in: OrgJoinRequestAudit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[bool]:
    """审批:通过/拒绝"""
    return OrgJoinRequestService(db).audit_request(
        request_id=request_id,
        reviewer_id=current_user.id,
        audit_in=audit_in
    )

@router.post("/{request_id}/cancel")
def cancel_resource_access_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Optional[bool]:
    """申请人取消自己待审批的申请"""
    return OrgJoinRequestService(db).cancel_request(
        request_id=request_id,
        applicant_user_id=current_user.id,
    )
