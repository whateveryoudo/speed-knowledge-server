from app.common.enums import ApprovalStatus, OrgType
from sqlalchemy.orm import Session
from app.models.org_join_request import OrgJoinRequest
from typing import Optional, Sequence


class OrgJoinRequestRepository:
    """组织审批请求数据访问层"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self, *, id: str, for_update: bool = False
    ) -> Optional[OrgJoinRequest]:
        query = self.db.query(OrgJoinRequest).filter(OrgJoinRequest.id == id)
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_pending(
        self, *, pending_key: str, for_update: bool = False
    ) -> Optional[OrgJoinRequest]:
        query = self.db.query(OrgJoinRequest).filter(
            OrgJoinRequest.pending_key == pending_key,
            OrgJoinRequest.status == ApprovalStatus.PENDING.value,
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def add(self, *, request: OrgJoinRequest) -> OrgJoinRequest:
        self.db.add(request)
        self.db.flush()
        return request

    def paginate_by_org(
        self,*,org_type: OrgType,org_id: str,status: Optional[ApprovalStatus] = None,
        page:int = 1, page_size:int = 20,
    ) -> tuple[Sequence[OrgJoinRequest], int, bool]:
        query = self.db.query(OrgJoinRequest).filter(
            OrgJoinRequest.org_type == org_type.value,
            OrgJoinRequest.org_id == org_id,
        )
        if status is not None:
            query = query.filter(OrgJoinRequest.status == status.value)
        query = query.order_by(OrgJoinRequest.created_at.desc())    
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        has_next = offset + page_size < total
        return items, total, has_next