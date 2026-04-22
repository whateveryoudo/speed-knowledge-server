from app.models.collect import Collect
from app.common.enums import CollectResourceType
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import joinedload
from typing import Optional
from app.common.enums import NotificationListType
from app.schemas.response import (
    PaginationResponse,
    PaginationQuery,
    paginate_query,
    paginate_response,
)
from app.models.notification import Notification
from fastapi import HTTPException, status
from app.schemas.notification import NotificationResponse, NotificationSearch
from app.models.user import User
from datetime import datetime


class NotificationService:
    """通知服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_notification_list(
        self, query_in: NotificationSearch
    ) -> PaginationResponse[NotificationResponse]:
        """获取通知列表"""

        query = (
            self.db.query(Notification)
            .join(
                [User, Notification.actor_user_id == User.id],
                [User, Notification.mentioned_user_id == User.id],
            )
            .options(
                joinedload(Notification.actor_user),
                joinedload(Notification.mentioned_user),
            )
        )
        filter_conditions = []

        if query_in.list_type:
            filter_conditions.append(Notification.list_type == query_in.list_type)
        if query_in.type == "unread":
            filter_conditions.append(Notification.read_at.is_(None))
        elif query_in.type == "read":
            filter_conditions.append(Notification.read_at.is_not(None))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"异常参数type: {query_in.type}",
            )
        if filter_conditions:
            query = query.filter(*filter_conditions)

        # 进行分页查询
        items, total, has_more = paginate_query(
            query, PaginationQuery(page=query_in.page, page_size=query_in.page_size)
        )  # 返回数据和总条数
        # 内容组合
        response_items = []
        for item in items:
            response_item = NotificationResponse(**item.model_dump())
            response_items.append(response_item)
        return paginate_response(response_items, total, has_more, query_in)

    def change_read_status(self, notification_id: str) -> bool:
        """修改通知已读状态"""
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"通知不存在: {notification_id}",
            )
        notification.read_at = datetime.now()
        self.db.commit()
        return True

    def count_unread_notifications_with_list_type(
        self, user_id: int, list_type: Optional[NotificationListType] = None
    ) -> dict[NotificationListType, int] | int | None:
        """统计未读通知数量(按列表类型返回)"""
        if list_type is not None:
            return (
                self.db.query(Notification)
                .filter(
                    Notification.mentioned_user_id == user_id,
                    Notification.read_at.is_(None),
                    Notification.list_type == list_type,
                )
                .count()
            )
        else:
            unread_rows = (
                self.db.query(Notification.list_type, func.count(Notification.id))
                .filter(
                    Notification.mentioned_user_id == user_id,
                    Notification.read_at.is_(None),
                )
                .group_by(Notification.list_type)
                .all()
            )
            result = {list_type: 0 for list_type in NotificationListType}
            for list_type, count in unread_rows:
                result[list_type] = count
            return result
