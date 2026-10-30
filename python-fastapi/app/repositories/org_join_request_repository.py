from app.common.enums import ApprovalStatus
from sqlalchemy.orm import Session
from app.models.org_join_request import OrgJoinRequest
from typing import Optional


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
        return OrgJoinRequest
