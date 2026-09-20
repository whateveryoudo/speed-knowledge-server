from sqlalchemy.orm import Session
from fastapi import HTTPException

from typing import List
from app.schemas.resource_collaboration import (
    ResourceCollaborationItem,
    ResourceCollaborationQuery,
)
from app.models.user import User
from app.schemas.resource_collaboration import CollaborationUserBrief
from app.repositories.resource_grant_repository import ResourceGrantRepository
from app.services.resource_grant_service import ResourceGrantService
from app.services.permission_service import PermissionService

from app.repositories.knowledge_repository import KnowledgeRepository
from app.common.enums import (
    PrincipalRole,
    SpaceType,
    ResourceType,
    PrincipalType,
    ResourceRole,
)
from app.models.resource_grant import ResourceGrant
from app.repositories.resource_access_request_repository import (
    ResourceAccessRequestRepository,
)

TEAM_ROLE_DISPLAY = {
    PrincipalRole.MEMBER: "团队成员",
    PrincipalRole.READONLY: "团队只读成员",
}

SPACE_ROLE_DISPLAY = {
    PrincipalRole.MEMBER: "空间成员",
    PrincipalRole.EXTERNAL: "空间外部联系人",
}


class ResourceCollaborationService:
    """资源协作服务(权限聚合页面)"""

    def __init__(self, db: Session):
        self.db = db
        self.grant_repository = ResourceGrantRepository(db)
        self.request_repository = ResourceAccessRequestRepository(db)
        self.knowledge_repository = KnowledgeRepository(db)
        self.permission_service = PermissionService(db)

    def _build_locked_admin_row(
        self, *, team_id: str, owner_grant: ResourceGrant | None, admin_grant: ResourceGrant | None
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

    def _build_editable_role_row(
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
            if g.principal_type == PrincipalType.TEAM_ROLE.value
            and g.principal_id == str(team_id)
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
                self._build_editable_role_row(
                    team_id=team_id,
                    role=role,
                    grant=team_grants.get(role),
                    can_manage=can_manage,
                )
            )
        return items

    @staticmethod
    def _to_user_brief(user: User | None) -> CollaborationUserBrief | None:
        """转换为用户简要信息"""
        if user is None:
            return None
        return CollaborationUserBrief(
            id=str(user.id),
            username=user.username,
            nickname=user.nickname,
        )

    @staticmethod
    def _to_user_display_name(user: User | None) -> str:
        """转换为用户显示名称"""
        if user is None:
            return "--"
        return user.nickname or user.username

    def _build_user_items(
        self, *, grants: List[ResourceGrant], creator_id: int | None, can_manage: bool
    ) -> List[ResourceCollaborationItem]:
        """构建用户授权项"""
        user_grants = [
            g
            for g in grants
            if g.principal_type == PrincipalType.USER.value
            and g.principal_role == PrincipalRole.NONE.value
        ]
        user_ids = [int(g.principal_id) for g in user_grants]
        # 这里还没有拆分repository，先直接sql查
        users = (
            self.db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
        )
        user_map = {user.id: user for user in users}
        items: List[ResourceCollaborationItem] = []
        for grant in user_grants:
            uid = int(grant.principal_id)
            user = user_map.get(uid) or None
            locked = creator_id is not None and uid == creator_id
            items.append(
                ResourceCollaborationItem(
                    row_type="user",
                    principal_type=PrincipalType.USER,
                    principal_id=str(uid),
                    principal_role=PrincipalRole.NONE,
                    user=self._to_user_brief(user),
                    display_name=self._to_user_display_name(user),
                    locked=locked,
                    resource_role=ResourceRole(grant.resource_role),
                    source=grant.source,
                    status="effective",
                    can_manage=can_manage and not locked,
                    grant_id=grant.id,
                    access_request_id=None,
                )
            )
        return items

    def _build_pending_items(
        self,
        *,
        resource_id: str,
        resource_type: ResourceType,
        can_manage: bool,
    ) -> List[ResourceCollaborationItem]:
        """构建进行中的访问请求"""
        items: List[ResourceCollaborationItem] = []
        access_requests = self.request_repository.list_pending_by_resource(
            resource_id=resource_id,
            resource_type=resource_type,
        )
        for access_request in access_requests:
            items.append(
                ResourceCollaborationItem(
                    row_type="pending",
                    principal_type=PrincipalType.USER,
                    principal_id=str(access_request.applicant_user_id),
                    principal_role=PrincipalRole.NONE,
                    user=self._to_user_brief(access_request.applicant),
                    display_name=self._to_user_display_name(access_request.applicant),
                    locked=False,
                    resource_role=ResourceRole(access_request.requested_role),
                    source="access_request",
                    status="pending",
                    can_manage=can_manage,
                    grant_id=None,
                    access_request_id=access_request.id,
                )
            )
        return items

    def _apply_filters(
        self, items: List[ResourceCollaborationItem], query: ResourceCollaborationQuery
    ) -> List[ResourceCollaborationItem]:
        """应用过滤条件"""
        keyword = (query.keyword or "").strip().lower()
        result: list[ResourceCollaborationItem] = []
        for item in items:
            if query.resource_role and item.resource_role != query.resource_role:
                # 不符合的角色
                continue
            if keyword and item.row_type in ("user", "pending"):
                # 角色类型授权不参与关键词过滤
                haystack = (item.display_name or "").lower()
                if item.user:
                    haystack += (
                        " "
                        + item.user.username.lower()
                        + " "
                        + (item.user.nickname or "").lower()
                    )
                if keyword not in haystack:
                    continue
            result.append(item)
        return result

    def _build_locked_space_admin_row(
        self,
        *,
        space_id: str,
        owner_grant: ResourceGrant | None,
        admin_grant: ResourceGrant | None,
    ) -> ResourceCollaborationItem:
        """构建锁定空间管理员行"""
        picked = admin_grant or owner_grant
        resource_role = ResourceRole.ADMIN if picked is not None else ResourceRole.NONE
        return ResourceCollaborationItem(
            row_type="role_group",
            principal_type=PrincipalType.SPACE_ROLE,
            principal_id=str(space_id),
            principal_role=PrincipalRole.ADMIN,
            user=None,
            display_name="空间管理员",
            locked=True,
            resource_role=resource_role,
            source=picked.source if picked is not None else None,
            status="effective",
            can_manage=False,
            grant_id=None,
            access_request_id=None,
        )

    def _build_editable_space_role_row(
        self,
        *,
        space_id: str,
        role: PrincipalRole,
        grant: ResourceGrant | None,
        can_manage: bool,
    ) -> ResourceCollaborationItem:
        """构建可编辑空间角色行"""
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
            principal_type=PrincipalType.SPACE_ROLE,
            principal_id=str(space_id),
            principal_role=role,
            user=None,
            display_name=SPACE_ROLE_DISPLAY[role],
            locked=False,
            resource_role=resource_role,
            source=source,
            status="effective",
            can_manage=can_manage,
            grant_id=grant_id,
            access_request_id=None,
        )

    def _build_space_role_items(
        self, *, space_id: str, grants: List[ResourceGrant], can_manage: bool
    ) -> List[ResourceCollaborationItem]:
        """构建空间授权项"""
        items: List[ResourceCollaborationItem] = []
        space_grants = {
            PrincipalRole(g.principal_role): g
            for g in grants
            if g.principal_type == PrincipalType.SPACE_ROLE.value
            and g.principal_id == str(space_id)
        }
        # 构建管理者项（Owner + Admin）
        items.append(
            self._build_locked_space_admin_row(
                space_id=space_id,
                owner_grant=space_grants.get(PrincipalRole.OWNER),
                admin_grant=space_grants.get(PrincipalRole.ADMIN),
            )
        )
        for role in (PrincipalRole.MEMBER, PrincipalRole.EXTERNAL):
            items.append(
                self._build_editable_space_role_row(
                    space_id=space_id,
                    role=role,
                    grant=space_grants.get(role),
                    can_manage=can_manage,
                )
            )
        # 构建成员项(这里包括成员和外来人)
        return items

    def list_knowledge_collaborations(
        self, *, knowledge_id: str, operator_id: int, query: ResourceCollaborationQuery
    ) -> List[ResourceCollaborationItem]:
        """获取资源协作"""
        self.permission_service.assert_can_manage_access_setting(
            operator_id, ResourceType.KNOWLEDGE, knowledge_id
        )
        knowledge = self.knowledge_repository.get_active_by_id(knowledge_id)
        if knowledge is None:
            raise HTTPException(status_code=404, detail="知识库不存在")

        grants = self.grant_repository.list_by_resource(
            resource_id=knowledge_id,
            resource_type=ResourceType.KNOWLEDGE,
        )

        items: List[ResourceCollaborationItem] = []

        if knowledge.team_id:
            # 构建团队授权项
            items.extend(
                self._build_team_role_items(
                    team_id=knowledge.team_id, grants=grants, can_manage=True
                )
            )
        elif (
            knowledge.space is not None
            and knowledge.space.type == SpaceType.ORGANIZATION.value
        ):
            # 构建空间授权项
            items.extend(
                self._build_space_role_items(
                    space_id=knowledge.space.id, grants=grants, can_manage=True
                )
            )
        # 构建用户授权行
        items.extend(
            self._build_user_items(
                grants=grants, creator_id=knowledge.creator_id, can_manage=True
            )
        )

        # 追加进行中的访问请求
        items.extend(
            self._build_pending_items(
                resource_id=knowledge_id,
                resource_type=ResourceType.KNOWLEDGE,
                can_manage=True,
            )
        )

        return self._apply_filters(items, query)
