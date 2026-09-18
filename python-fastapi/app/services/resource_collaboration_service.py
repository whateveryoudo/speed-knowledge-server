from sqlalchemy.orm import Session
from fastapi import HTTPException

from typing import List
from app.schemas.resource_collaboration import (
    ResourceCollaborationItem,
    ResourceCollaborationQuery,
)
from app.repositories.resource_grant_repository import ResourceGrantRepository
from app.services.resource_grant_service import ResourceGrantService
from app.services.permission_service import PermissionService
from app.repositories.knowledge_repository import KnowledgeRepository
from app.common.enums import PrincipalRole, ResoureType, PrincipalType, ResourceRole
from app.models.resource_grant import ResourceGrant
from app.repositories.resource_access_request_repository import (
    ResourceAccessRequestRepository,
)

TEAM_ROLE_DISPLAY = {
    PrincipalRole.MEMBER: "团队成员",
    PrincipalRole.READONLY: "团队只读成员",
}


class ResourceCollaborationService:
    """资源协作服务(权限聚合页面)"""

    def __init__(self, db: Session):
        self.db = db
        self.grant_repository = ResourceGrantRepository(db)
        self.request_repository = ResourceAccessRequestRepository(db)
        self.knowledge_repository = KnowledgeRepository(db)
        self.grent_service = ResourceGrantService(db)
        self.permission_service = PermissionService(db)

    def _build_locked_admin_row(
        self, team_id: str, owner_grant: ResourceGrant, admin_grant: ResourceGrant
    ) -> ResourceCollaborationItem:
        """构建锁定管理员行(这里对owner + admin 进行合并，库里还是两条grant)"""
        picked = admin_grant or owner_grant
        resource_role = ResourceRole.ADMIN if picked is not None else ResourceRole.NONE
        return ResourceCollaborationItem(
            row_type="role_group",
            principal_type=PrincipalType.TEAM_ROLE,
            principal_id=str(team_id),
            principal_role=PrincipalRole.ADMIN,
            user=None,
            display_name="团队管理员",
            locked=True,
            resource_role=resource_role,
            source=picked.source if picked is not None else None,
            status="effective",
            can_manage=False,
            grant_id=None,
            access_request_id=None,
        )

    def _buil_editable_role_row(
        self,
        team_id: str,
        role: PrincipalRole,
        grant: ResourceGrant | None,
        can_manage: bool,
    ) -> ResourceCollaborationItem:
        """构建可编辑角色行"""
        if grant is not None:
            resource_role = ResourceRole(grant.resource_role)
            grant_id = grant.id
            source = grant.source
        else:
            resource_role = ResourceRole.NONE
            grant_id = None
            source = None
        return ResourceCollaborationItem(
            row_type="role_group",
            principal_type=PrincipalType.TEAM_ROLE,
            principal_id=str(team_id),
            principal_role=role,
            user=None,
            display_name=TEAM_ROLE_DISPLAY[role],
            locked=False,
            resource_role=resource_role,
            source=source,
            status="effective",
            can_manage=can_manage,
            grant_id=grant_id,
            access_request_id=None,
        )

    def _build_team_role_items(
        self, team_id: str, grants: List[ResourceGrant], can_manage: bool
    ) -> List[ResourceCollaborationItem]:
        """构建团队授权项"""
        items: List[ResourceCollaborationItem] = []
        team_grants = {
            PrincipalRole(g.principal_role): g
            for g in grants
            if g.principal_type == PrincipalType.TEAM and g.principal_id == str(team_id)
        }

        items = [
            self._build_locked_admin_row(
                team_id=team_id,
                owner_grant=team_grants.get(PrincipalRole.OWNER),
                admin_grant=team_grants.get(PrincipalRole.ADMIN),
            )
        ]

        for role in (PrincipalRole.MEMBER, PrincipalRole.READONLY):
            items.append(
                self._buil_editable_role_row(
                    team_id=team_id,
                    role=role,
                    grant=team_grants.get(role),
                    can_manage=can_manage,
                )
            )
        return items

    def list_knowledge_collaborations(
        self, *, knowledge_id: str, operator_id: str, query: ResourceCollaborationQuery
    ) -> List[ResourceCollaborationItem]:
        """获取资源协作"""
        self.permission_service.assert_can_manage_access_setting(
            operator_id, ResoureType.KNOWLEDGE, knowledge_id
        )
        knowledge = self.knowledge_repository.get_knowledge_by_id(knowledge_id)
        if knowledge is None:
            raise HTTPException(status_code=404, detail="知识库不存在")

        grants = self.grant_repository.list_by_resource(
            resource_id=knowledge_id,
            resource_type=ResoureType.KNOWLEDGE,
        )

        items: List[ResourceCollaborationItem] = []

        if knowledge.team_id:
            # 构建团队授权项
            items.extend(
                self._build_team_role_items(
                    team_id=knowledge.team_id, grants=grants, can_manage=True
                )
            )
