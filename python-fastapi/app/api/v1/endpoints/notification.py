from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse, NotificationSearch
from app.schemas.response import PaginationResponse
from app.common.enums import NotificationListType


router = APIRouter()


@router.get(
    "/list",
    response_model=PaginationResponse[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
def get_notifications(
    query_in: NotificationSearch = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse[NotificationResponse]:
    """获取通知列表(分页按照类型查询)"""
    notification_service = NotificationService(db)
    temp_query = query_in.model_copy(update={"user_id": current_user.id})
    notifications = notification_service.get_notification_list(temp_query)
    return notifications


@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
def change_read_status(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """修改为已读"""
    notification_service = NotificationService(db)
    return notification_service.change_read_status(notification_id)


@router.get(
    "/all-unread-count",
    response_model=dict[NotificationListType, int],
    status_code=status.HTTP_200_OK,
)
def get_all_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[NotificationListType, int]:
    """获取通知数量(按列表类型返回)"""
    notification_service = NotificationService(db)
    return notification_service.count_unread_notifications_with_list_type(
        current_user.id
    )


@router.get("/{list_type}/unread-count", response_model=int, status_code=status.HTTP_200_OK)
def get_unread_count_by_list_type(
    list_type: NotificationListType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    """获取指定列表类型的未读通知数量"""
    notification_service = NotificationService(db)
    return notification_service.count_unread_notifications_with_list_type(
        current_user.id, list_type
    )
