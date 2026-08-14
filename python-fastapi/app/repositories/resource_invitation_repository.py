from app.models.resource_invitation import ResourceInvitation
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session
from app.common.enums import InvitationStatus, ResourceType


class ResourceInvitationRepository(BaseRepository[ResourceInvitation]):
    """资源邀请数据访问（知识库/文档）"""

    def __init__(self, db: Session):
        super().__init__(db, ResourceInvitation)

    def get_by_id(
        self, *, invitation_id: str, for_update: bool = False
    ) -> ResourceInvitation | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(ResourceInvitation.id == invitation_id).first()

    def get_active_by_token(
        self, token: str, *, for_update: bool = False
    ) -> ResourceInvitation | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(
            ResourceInvitation.token == token,
            ResourceInvitation.status == InvitationStatus.ACTIVE.value,
        ).first()

    def get_by_resource(
        self, *, resource_type: ResourceType, resource_id: str, for_update: bool = False
    ) -> ResourceInvitation | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(
            ResourceInvitation.resource_type == resource_type.value,
            ResourceInvitation.resource_id == str(resource_id),
        ).first()

    def token_exists(self, token: str) -> bool:
        return self.all_query().filter(ResourceInvitation.token == token).first() is not None
