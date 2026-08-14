"""资源访问申请路由（这里其实是一些审批相关的（目前和页面关联的只有pending状态下的数据））"""

from fastapi import APIRouter, Depends
from app.services.permission_service import PermissionService
from app.common.enums import ResourceType
from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.resource_access_request import (
    ResourceAccessRequestQuery,
    ResourceAccessRequestResponse,
    ResourceAccessRequestListItem,
)
from app.core.deps import get_current_user, get_db
from app.schemas.response import PaginationResponse
from app.services.resource_access_request_service import ResourceAccessRequestService

router = APIRouter()


def _assert_can_review_request(
    *, db: Session, reviewer_id: int, resource_type: ResourceType, resource_id: str
) -> None:
    """校验用户是否有权管理该资源的申请"""
    PermissionService(db).assert_can_manage_access_setting(
        reviewer_id, resource_type, resource_id
    )


@router.get(
    "/resource/{resource_type}/{resource_id}",
    response_model=PaginationResponse[ResourceAccessRequestListItem],
)
def get_resource_access_requests(
    resource_type: ResourceType,
    resource_id: str,
    db: Session = Depends(get_db),
    query_in: ResourceAccessRequestQuery = Depends(),
    current_user: User = Depends(get_current_user),
) -> PaginationResponse[ResourceAccessRequestListItem]:
    """获取指定资源的访问申请列表"""
    _assert_can_review_request(
        db=db,
        reviewer_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    return ResourceAccessRequestService(db).get_requests_by_resource(
        resource_type=resource_type,
        resource_id=resource_id,
        query_in=query_in,
    )


@router.post("/{request_id}/approve", response_model=ResourceAccessRequestResponse)
def approve_resource_access_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceAccessRequestResponse:
    """审批通过"""
    service = ResourceAccessRequestService(db)
    access_request = service.get_by_id_or_404(request_id)
    _assert_can_review_request(
        db=db,
        reviewer_id=current_user.id,
        resource_type=ResourceType(access_request.resource_type),
        resource_id=access_request.resource_id,
    )
    try:
        access_request = service.approve_request(
            request_id=request_id,
            reviewer_id=current_user.id,
        )
        db.commit()
        db.refresh(access_request)
        return access_request
    except Exception:
        db.rollback()
        raise


@router.post("/{request_id}/reject", response_model=ResourceAccessRequestResponse)
def reject_resource_access_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceAccessRequestResponse:
    """审批拒绝"""
    service = ResourceAccessRequestService(db)
    access_request = service.get_by_id_or_404(request_id)
    _assert_can_review_request(
        db=db,
        reviewer_id=current_user.id,
        resource_type=ResourceType(access_request.resource_type),
        resource_id=access_request.resource_id,
    )
    try:
        access_request = service.reject_request(
            request_id=request_id,
            reviewer_id=current_user.id,
        )
        db.commit()
        db.refresh(access_request)
        return access_request
    except Exception:
        db.rollback()
        raise


@router.post("/{request_id}/cancel", response_model=ResourceAccessRequestResponse)
def cancel_resource_access_request(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResourceAccessRequestResponse:
    """申请人取消自己待审批的申请"""
    service = ResourceAccessRequestService(db)
    try:
        access_request = service.cancel_request(
            request_id=request_id,
            applicant_user_id=current_user.id,
        )
        db.commit()
        db.refresh(access_request)
        return access_request
    except Exception:
        db.rollback()
        raise
