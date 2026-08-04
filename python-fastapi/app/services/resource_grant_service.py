from QwenPaw.tests.unit.agents.context.test_scroll_manager import user
from app.models.resource_grant import ResourceGrant
from sqlalchemy.orm import Session
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.common.enums.resource_grant import (
    PrincipalType,
    PrincipalRole,
    ResourceType,
    GrantSource,
    ResourceRole,
)
from app.common.enums.knowledge import KnowledgeVisibility
from app.models.team_member import TeamMember
from app.models.space_member import SpaceMember
from app.common.enums.space import SpaceType


class ResourceGrantService:
    ROLE_PRIORITY = {
        ResourceRole.ADMIN: 30,
        ResourceRole.EDIT: 20,
        ResourceRole.READ: 10,
    }
    VALID_PRINCIPAL_ROLES = {
        PrincipalType.USER: {
            PrincipalRole.NONE,
        },
        PrincipalType.SPACE_ROLE: {
            PrincipalRole.OWNER,
            PrincipalRole.ADMIN,
            PrincipalRole.MEMBER,
            PrincipalRole.EXTERNAL,
        },
        PrincipalType.TEAM_ROLE: {
            PrincipalRole.OWNER,
            PrincipalRole.ADMIN,
            PrincipalRole.MEMBER,
            PrincipalRole.READONLY,
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def get_highest_role(self, roles: list[ResourceRole]) -> ResourceRole | None:
        """获取最高角色"""
        if not roles:
            return None
        return max(roles, key=lambda x: self.ROLE_PRIORITY[x])

    def resolve_effective_role(
        self,
        *,
        user_id: int | None,
        resource_type: ResourceType,
        resource_id: str,
        team_id: str | None,
        space_id: str,
        is_public: bool,
    ) -> ResourceRole:
        """计算用户对一个知识库的最终资源角色。"""
        # 获取当前资源的所有授权
        grants = (
            self.db.query(ResourceGrant)
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == resource_id,
            )
            .all()
        )
        matched_grants: list[ResourceRole] = []
        # 计算最终角色
        if is_public:
            matched_grants.append(ResourceRole.READ)

        if user_id is None:
            # 如果未登录直接按照游客模式
            return self.get_highest_role(matched_grants)

        user_id_value = str(user_id)
        # 直接授权
        for grant in grants:
            if (
                grant.principal_type == PrincipalType.USER.value
                and grant.principal_role == PrincipalRole.NONE.value
                and grant.principal_id == user_id_value
            ):
                matched_grants.append(ResourceRole(grant.resource_role))
        # 团队继承
        team_role_grants = [
            grant
            for grant in grants
            if grant.principal_type == PrincipalType.TEAM_ROLE.value
            and grant.principal_id == team_id
        ]
        if team_id is not None and team_role_grants:
            team_member = (
                self.db.query(TeamMember)
                .filter(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id,
                )
                .first()
            )
            if team_member is None:
                team_member_role = (
                    team_member.role.value
                    if hasattr(team_member.role, "value")
                    else team_member.role
                )
                for grant in team_role_grants:
                    if grant.principal_role == team_member_role:
                        matched_grants.append(ResourceRole(grant.resource_role))

        # 空间继承
        space_role_grants = [
            grant
            for grant in grants
            if grant.principal_type == PrincipalType.SPACE_ROLE.value
            and grant.principal_id == space_id
        ]
        if space_role_grants:
            space_member = (
                self.db.query(SpaceMember)
                .filter(
                    SpaceMember.space_id == space_id,
                    SpaceMember.user_id == user_id,
                )
                .first()
            )
            if space_member is None:
                space_member_role = (
                    space_member.role.value
                    if hasattr(space_member.role, "value")
                    else space_member.role
                )
                for grant in space_role_grants:
                    if grant.principal_role == space_member_role:
                        matched_grants.append(ResourceRole(grant.resource_role))
        return self.get_highest_role(matched_grants)

    def resolve_granted_knowledge_role(
        self,
        *,
        user_id: int | None,
        knowledge: Knowledge,
    ) -> ResourceRole | None:
        """计算用户对一个知识库的最终资源角色。"""
        return self.resolve_effective_role(
            user_id=user_id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            team_id=knowledge.team_id,
            space_id=knowledge.space_id,
            is_public=False,
        )

    def resolve_granted_document_role(
        self,
        *,
        user_id: int | None,
        document: Document,
    ) -> ResourceRole | None:
        """计算用户对一个文档的最终资源角色。"""
        return self.resolve_effective_role(
            user_id=user_id,
            resource_type=ResourceType.DOCUMENT,
            resource_id=document.id,
            team_id=document.knowledge.team_id,
            space_id=document.knowledge.space_id,
            is_public=False,
        )

    def role_covers(
        self, current_role: ResourceRole | None, requested_role: ResourceRole
    ) -> bool:
        """判断当前角色是否覆盖请求角色"""
        if current_role is None:
            return False
        return self.ROLE_PRIORITY[current_role] >= self.ROLE_PRIORITY[requested_role]

    def _validate_principal_role(
        self, principal_type: PrincipalType, principal_role: PrincipalRole
    ) -> None:
        """验证主体角色"""
        allowed_roles = self.VALID_PRINCIPAL_ROLES[principal_type]
        if principal_role not in allowed_roles:
            raise ValueError(
                f"Invalid principal role: {principal_role} for principal type: {principal_type}"
            )

    def upsert_grant(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        principal_type: PrincipalType,
        principal_id: str | int,
        principal_role: PrincipalRole,
        resource_role: ResourceRole,
        source: GrantSource,
        created_by: int | None,
    ) -> ResourceGrant | None:
        """更新/创建授权"""

        self._validate_principal_role(principal_type, principal_role)
        principal_id_value = str(principal_id)
        grant = (
            self.db.query(ResourceGrant)
            .filter(
                ResourceGrant.resource_type == resource_type.value,
                ResourceGrant.resource_id == resource_id,
                ResourceGrant.principal_type == principal_type.value,
                ResourceGrant.principal_id == principal_id_value,
                ResourceGrant.principal_role == principal_role.value,
            )
            .first()
        )
        if resource_role == ResourceRole.NONE:
            if grant is not None:
                self.db.delete(grant)
                self.db.flush()
            return None

        if grant is None:
            grant = ResourceGrant(
                resource_type=resource_type.value,
                resource_id=resource_id,
                principal_type=principal_type.value,
                principal_id=principal_id_value,
                principal_role=principal_role.value,
                resource_role=resource_role.value,
                source=source.value,
                created_by=created_by,
            )
            self.db.add(grant)
        else:
            grant.resource_role = resource_role.value
            grant.source = source.value
            grant.created_by = created_by
        self.db.flush()
        # 这里不commit
        return grant

    def create_creator_grant(
        self, *, knowledge: Knowledge, creator_id: int
    ) -> ResourceGrant:
        """创建创建者授权"""
        return self.upsert_grant(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            principal_type=PrincipalType.USER,
            principal_id=creator_id,
            principal_role=PrincipalRole.NONE,
            resource_role=ResourceRole.ADMIN,
            source=GrantSource.CREATOR,
            created_by=creator_id,
        )

    def create_team_grant(
        self, *, knowledge: Knowledge, created_by: int
    ) -> list[ResourceGrant]:
        """创建团队授权"""
        if not knowledge.team_id:
            raise ValueError("Knowledge team_id is required")
        # 进行权限映射操作
        mappings = {
            PrincipalRole.OWNER: ResourceRole.ADMIN,
            PrincipalRole.ADMIN: ResourceRole.ADMIN,
            PrincipalRole.MEMBER: ResourceRole.EDIT,
            PrincipalRole.READONLY: ResourceRole.READ,
        }
        return [
            self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.TEAM_ROLE,
                principal_id=knowledge.team_id,
                principal_role=principal_role,
                resource_role=resource_role,
                source=GrantSource.DEFAULT_POLICY,
                created_by=created_by,
            )
            for principal_role, resource_role in mappings.items()
        ]

    # 这里对空间授权，拆分成两个方法
    def create_space_admin_grant(
        self, *, knowledge: Knowledge, created_by: int
    ) -> list[ResourceGrant]:
        """创建空间管理员授权"""
        mappings = {
            PrincipalRole.OWNER: ResourceRole.ADMIN,
            PrincipalRole.ADMIN: ResourceRole.ADMIN,
        }
        grants = []
        for principal_role, resource_role in mappings.items():
            grant = self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.SPACE_ROLE,
                principal_id=knowledge.space_id,
                principal_role=principal_role,
                resource_role=resource_role,
                source=GrantSource.DEFAULT_POLICY,
                created_by=created_by,
            )
            if grant is None:
                raise RuntimeError(f"空间管理员默认授权不能为空")
            grants.append(grant)
        return grants

    def create_space_member_visibility_grant(
        self, *, knowledge: Knowledge, created_by: int
    ) -> list[ResourceGrant]:
        """创建空间成员授权"""
        grant = self.upsert_grant(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            principal_type=PrincipalType.SPACE_ROLE,
            principal_id=knowledge.space_id,
            principal_role=PrincipalRole.MEMBER,
            resource_role=ResourceRole.READ,
            source=GrantSource.DEFAULT_POLICY,
            created_by=created_by,
        )
        if grant is None:
            raise RuntimeError(f"空间成员默认授权不能为空")
        return grant

    def create_space_grant(
        self, *, knowledge: Knowledge, created_by: int
    ) -> list[ResourceGrant]:
        """创建空间授权"""
        mappings = {
            PrincipalRole.OWNER: ResourceRole.ADMIN,
            PrincipalRole.ADMIN: ResourceRole.ADMIN,
            PrincipalRole.MEMBER: ResourceRole.EDIT,
        }
        return [
            self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.SPACE_ROLE,
                principal_id=knowledge.space_id,
                principal_role=principal_role,
                resource_role=resource_role,
                source=GrantSource.DEFAULT_POLICY,
                created_by=created_by,
            )
            for principal_role, resource_role in mappings.items()
        ]

    def create_default_knowledge_grants(
        self, *, knowledge: Knowledge, creator_id: int
    ) -> list[ResourceGrant]:
        """创建默认授权"""
        grants = [
            self.create_creator_grant(
                knowledge=knowledge,
                creator_id=creator_id,
            )
        ]

        if knowledge.team_id:
            grants.extend(
                self.create_team_grant(
                    knowledge=knowledge,
                    created_by=creator_id,
                )
            )
            return grants

        if knowledge.space.type != SpaceType.ORGANIZATION:
            # 个人空间
            return grants
        # 增加空间管理员授权
        grants.extend(
            self.create_space_admin_grant(
                knowledge=knowledge,
                created_by=creator_id,
            )
        )
        # 仅当空间成员可见才继承空间角色
        if knowledge.visibility == KnowledgeVisibility.SPACE.value:
            grants.extend(
                self.create_space_member_visibility_grant(
                    knowledge=knowledge,
                    created_by=creator_id,
                )
            )
        return grants

    def delete_space_member_visibility_grant(self, *, knowledge: Knowledge) -> None:
        """删除空间成员授权"""
        self.db.query(ResourceGrant).filter(
            ResourceGrant.resource_type == ResourceType.KNOWLEDGE.value,
            ResourceGrant.resource_id == knowledge.id,
            ResourceGrant.principal_type == PrincipalType.SPACE_ROLE.value,
            ResourceGrant.principal_id == knowledge.space.id,
            ResourceGrant.principal_role == PrincipalRole.MEMBER.value,
        ).delete(synchronize_session=False)
        self.db.flush()

    def sync_knowledge_visibility_grants(
        self,
        *,
        knowledge: Knowledge,
        old_visibility: KnowledgeVisibility,
        new_visibility: KnowledgeVisibility,
        operator_id: int,
    ) -> None:
        """同步可见范围授权"""
        is_space_public_area = (
            knowledge.team_id is None and knowledge.space.type == SpaceType.ORGANIZATION
        )
        if not is_space_public_area:
            return

        # space -> private/public,需要空间成员的已有授权
        if old_visibility == KnowledgeVisibility.SPACE:
            self.delete_space_member_visibility_grant(knowledge=knowledge)
        # private/public -> space,需要空间成员的已有授权
        if new_visibility == KnowledgeVisibility.SPACE:
            self.create_space_member_visibility_grant(
                knowledge=knowledge,
                created_by=operator_id,
            )
