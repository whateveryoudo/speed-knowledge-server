"""资源访问申请数据访问"""

from sqlalchemy.orm import Session, joinedload
from app.models.resource_access_request import ResourceAccessRequest
from app.repositories.base_repository import BaseRepository
from app.common.enums import AccessRequestStatus, ResourceType


class ResourceAccessRequestRepository(BaseRepository[ResourceAccessRequest]):
    """仅提供数据库层面的读写"""

    def __init__(self, db: Session):
        super().__init__(db, ResourceAccessRequest)

    def get_by_id(
        self, request_id: str, *, for_update: bool = False
    ) -> ResourceAccessRequest | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(ResourceAccessRequest.id == request_id).first()

    def get_pending(
        self, *, pending_key: str, for_update: bool = False
    ) -> ResourceAccessRequest | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(
            ResourceAccessRequest.pending_key == pending_key,
            ResourceAccessRequest.status == AccessRequestStatus.PENDING.value,
        ).first()

    def list_pending_by_resource(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> list[ResourceAccessRequest]:
        return (
            self.all_query()
            .options(
                joinedload(ResourceAccessRequest.applicant),
                joinedload(ResourceAccessRequest.reviewed_user),
            )
            .filter(
                ResourceAccessRequest.resource_type == resource_type.value,
                ResourceAccessRequest.resource_id == str(resource_id),
                ResourceAccessRequest.status == AccessRequestStatus.PENDING.value,
            )
            .order_by(ResourceAccessRequest.created_at.desc())
            .all()
        )

    def paginate_by_resource(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        status: AccessRequestStatus | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[ResourceAccessRequest], int, bool]:
        """获取资源审批历史分页（目前还用不上）"""
        query = (
            self.all_query()
            .options(
                joinedload(ResourceAccessRequest.applicant),
                joinedload(ResourceAccessRequest.reviewed_user),
            )
            .filter(
                ResourceAccessRequest.resource_type == resource_type.value,
                ResourceAccessRequest.resource_id == str(resource_id),
            )
        )
        if status is not None:
            query = query.filter(ResourceAccessRequest.status == status.value)

        total = query.count()
        offset = (page - 1) * page_size

        items = (
            query.order_by(ResourceAccessRequest.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        has_more = total > offset + len(items)

        return items, total, has_more

    def paginate_by_applicant(
        self,
        *,
        applicant_user_id: int,
        status: AccessRequestStatus | None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[ResourceAccessRequest], int, bool]:
        """获取申请人自己的审批历史分页"""
        query = (
            self.all_query()
            .options(
                joinedload(ResourceAccessRequest.applicant),
                joinedload(ResourceAccessRequest.reviewed_user),
            )
            .filter(ResourceAccessRequest.applicant_user_id == applicant_user_id)
        )

        if status is not None:
            query = query.filter(ResourceAccessRequest.status == status.value)

        total = query.count()
        offset = (page - 1) * page_size

        items = (
            query.order_by(ResourceAccessRequest.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        has_more = total > offset + len(items)

        return items, total, has_more
