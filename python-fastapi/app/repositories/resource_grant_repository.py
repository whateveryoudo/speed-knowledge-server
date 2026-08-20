"""资源授权的数据访问"""

from sqlalchemy.orm import Session
from app.models.resource_grant import ResourceGrant
from app.repositories.base_repository import BaseRepository
from typing import Sequence
from sqlalchemy import and_, or_
from app.common.enums import ResourceType, PrincipalType, PrincipalRole


class ResourceGrantRepository(BaseRepository[ResourceGrant]):
    """仅提供数据库层面的读写"""

    def __init__(self, db: Session):
        super().__init__(db, ResourceGrant)

    def get_by_id(
        self, grant_id: str, *, for_update: bool = False
    ) -> ResourceGrant | None:
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(ResourceGrant.id == grant_id).first()

    def get_by_principal(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        principal_type: PrincipalType,
        principal_role: PrincipalRole,
        principal_id: int | str,
        for_update: bool = False,
    ) -> ResourceGrant | None:
        """根据授权主体定位grant"""
        query = self.all_query()
        if for_update:
            query = query.with_for_update()
        return query.filter(
            ResourceGrant.resource_type == resource_type.value,
            ResourceGrant.resource_id == str(resource_id),
            ResourceGrant.principal_type == principal_type.value,
            ResourceGrant.principal_role == principal_role.value,
            ResourceGrant.principal_id == str(principal_id),
        ).first()

    def list_by_resource(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> list[ResourceGrant]:
        return (
            self.all_query()
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == str(resource_id),
            )
            .order_by(ResourceGrant.created_at.desc())
            .all()
        )

    def list_by_resources(
        self, *, resource_type: ResourceType, resource_ids: Sequence[str]
    ) -> list[ResourceGrant]:
        if not resource_ids:
            return []
        return (
            self.all_query()
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id.in_(
                    [str(resource_id) for resource_id in resource_ids]
                ),
            )
            .all()
        )

    def list_resource_ids_by_principals(
        self,
        *,
        resource_type: ResourceType,
        principals: Sequence[tuple[PrincipalType, int | str, PrincipalRole]],
    ) -> list[str]:
        """获取主体的资源ID列表"""
        if not principals:
            return []
        principal_conditions = [
            and_(
                ResourceGrant.principal_type == principal_type.value,
                ResourceGrant.principal_role == principal_role.value,
                ResourceGrant.principal_id == str(principal_id),
            )
            for (principal_type, principal_id, principal_role) in principals
        ]
        rows = (
            self.all_query()
            .with_entities(ResourceGrant.resource_id)
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                or_(*principal_conditions),
            )
            .distinct()
            .all()
        )
        return [resource_id for (resource_id,) in rows]

    def list_direct_user_grants(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> list[ResourceGrant]:
        """获取资源的直接用户授权"""
        return (
            self.all_query()
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == str(resource_id),
                ResourceGrant.principal_type == PrincipalType.USER.value,
                ResourceGrant.principal_role == PrincipalRole.NONE.value,
            )
            .all()
        )

    def delete_by_principal(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        principal_type: PrincipalType,
        principal_role: PrincipalRole,
        principal_id: int | str,
    ) -> int:
        """删除资源上某个主体的全部授权"""
        return (
            self.all_query()
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == str(resource_id),
                ResourceGrant.principal_type == principal_type.value,
                ResourceGrant.principal_role == principal_role.value,
                ResourceGrant.principal_id == str(principal_id),
            )
            .delete(synchronize_session=False)
        )

    def delete_by_resource(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> int:
        """删除指定资源的全部授权，返回影响行数(知识库/文档彻底删除时使用)"""
        return (
            self.all_query()
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == str(resource_id),
            )
            .delete(synchronize_session=False)
        )
