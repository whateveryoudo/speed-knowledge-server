from sqlalchemy.orm import joinedload
from app.common.enums import OrgType
from sqlalchemy.orm import Session
from app.models.org_invitation import OrgInvitation
from typing import Optional


class OrgInvitationRepository:
    """组织邀请数据访问层"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user(
        self,
        *,
        org_type: OrgType,
        org_id: str,
        inviter_id: int,
        for_update: bool = False,
    ) -> Optional[OrgInvitation]:
        query = self.db.query(OrgInvitation).filter(
            OrgInvitation.org_id == org_id,
            OrgInvitation.org_type == org_type.value,
            OrgInvitation.inviter_id == inviter_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_by_token(
        self, *, invite_token: str, for_update: bool = False
    ) -> Optional[OrgInvitation]:
        query = (
            self.db.query(OrgInvitation)
            .options(joinedload(OrgInvitation.inviter))
            .filter(OrgInvitation.invite_token == invite_token)
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def add(self, *, invitation: OrgInvitation) -> OrgInvitation:
        self.db.add(invitation)
        self.db.flush()
        return invitation
