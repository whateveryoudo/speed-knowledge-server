from app.models.permission_group import PermissionGroup
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session, joinedload
from app.common.enums import PermissionScopeType
from typing import Sequence


class PermissionGroupRepository(BaseRepository[PermissionGroup]):
    """PermissionGroup数据访问"""

    def __init__(self, db: Session):
        super().__init__(db, PermissionGroup)

    def get_by_id(self, group_id: str) -> PermissionGroup | None:
        return (
            self.all_query()
            .options(joinedload(PermissionGroup.abilities))
            .filter(PermissionGroup.id == group_id)
            .first()
        )

    def get_by_scope_role(
        self,
        *,
        scope_type: PermissionScopeType,
        scope_id: str,
        role_key: str,
    ) -> PermissionGroup | None:
        return (
            self.all_query()
            .options(joinedload(PermissionGroup.abilities))
            .filter(
                PermissionGroup.scope_type == scope_type.value,
                PermissionGroup.scope_id == str(scope_id),
                PermissionGroup.role_key == role_key,
            )
            .first()
        )

    def list_by_scope(
        self, *, scope_type: PermissionScopeType, scope_id: str
    ) -> list[PermissionGroup]:
        return (
            self.all_query()
            .options(joinedload(PermissionGroup.abilities))
            .filter(
                PermissionGroup.scope_type == scope_type.value,
                PermissionGroup.scope_id == str(scope_id),
            )
            .all()
        )

    def list_by_scopes(
        self,
        *,
        scope_type: PermissionScopeType,
        scope_ids: Sequence[str],
    ) -> list[PermissionGroup]:
        if not scope_ids:
            return []
        return (
            self.all_query()
            .options(joinedload(PermissionGroup.abilities))
            .filter(
                PermissionGroup.scope_type == scope_type.value,
                PermissionGroup.scope_id.in_([str(scope_id) for scope_id in scope_ids]),
            )
            .all()
        )

    def delete_by_scope(
        self, *, scope_type: PermissionScopeType, scope_id: str
    ) -> int:
        return (
            self.all_query()
            .filter(
                PermissionGroup.scope_type == scope_type.value,
                PermissionGroup.scope_id == str(scope_id),
            )
            .delete(synchronize_session=False)
        )
