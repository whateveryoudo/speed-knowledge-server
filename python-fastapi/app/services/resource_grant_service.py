from app.models.resource_grant import ResourceGrant
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.common.enums import (
    PrincipalType,
    PrincipalRole,
    ResourceType,
    GrantSource,
    ResourceRole,
    KnowledgeVisibility,
    SpaceType,
)
from app.models.team_member import TeamMember
from app.models.space_member import SpaceMember
from app.repositories.resource_grant_repository import ResourceGrantRepository
from app.common.utils import is_duplicate_on


class ResourceGrantService:
    GRANT_UNIQUE_CONSTRAINT = "uniq_resource_grant"

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
        self.grant_repository = ResourceGrantRepository(db)

    def get_highest_role(self, roles: list[ResourceRole]) -> ResourceRole | None:
        """获取最高角色"""
        if not roles:
            return None
        return max(roles, key=lambda x: self.ROLE_PRIORITY[x])

    def resolve_multiple_granted_knowledge_roles(
        self, *, user_id: int, knowledges: list[Knowledge]
    ) -> dict[str, ResourceRole | None]:
        """批量获取知识库的最终角色"""
        if not knowledges:
            return {}
        knowledge_ids = [knowledge.id for knowledge in knowledges]
        grants = self.grant_repository.list_by_resources(
            resource_type=ResourceType.KNOWLEDGE,
            resource_ids=knowledge_ids,
        )
        # 理解下difaultdict（访问不存在的key会自动创建一个空的list,否则直接append回提示KeyError）
        grants_by_resource: dict[str, list[ResourceGrant]] = defaultdict(list)
        for grant in grants:
            grants_by_resource[grant.resource_id].append(grant)
        team_ids = {
            knowledge.team_id
            for knowledge in knowledges
            if knowledge.team_id is not None
        }
        space_ids = {knowledge.space_id for knowledge in knowledges}
        team_members: list[TeamMember] = []
        space_members: list[SpaceMember] = []
        if team_ids:
            team_members = (
                self.db.query(TeamMember)
                .filter(
                    TeamMember.team_id.in_(team_ids),
                    TeamMember.user_id == user_id,
                )
                .all()
            )
        if space_ids:
            space_members = (
                self.db.query(SpaceMember)
                .filter(
                    SpaceMember.space_id.in_(space_ids),
                    SpaceMember.user_id == user_id,
                )
                .all()
            )

        team_role_by_team_id = {
            member.team_id: member.role.value for member in team_members
        }

        space_role_by_space_id = {
            member.space_id: member.role.value for member in space_members
        }
        user_id_value = str(user_id)
        result: dict[str, ResourceRole | None] = {}
        for knowledge in knowledges:
            merged_roles: list[ResourceRole] = []
            if knowledge.visibility == KnowledgeVisibility.PUBLIC.value:
                merged_roles.append(ResourceRole.READ)
            team_role = team_role_by_team_id.get(knowledge.team_id)
            space_role = space_role_by_space_id.get(knowledge.space_id)
            for grant in grants_by_resource.get(knowledge.id, []):
                # 用户直接授权
                if (
                    grant.principal_type == PrincipalType.USER.value
                    and grant.principal_role == PrincipalRole.NONE.value
                    and grant.principal_id == user_id_value
                ):
                    merged_roles.append(ResourceRole(grant.resource_role))
                    continue
                # 团队角色继承
                if (
                    knowledge.team_id is not None
                    and team_role is not None
                    and grant.principal_type == PrincipalType.TEAM_ROLE.value
                    and grant.principal_id == str(knowledge.team_id)
                    and grant.principal_role == team_role
                ):
                    merged_roles.append(ResourceRole(grant.resource_role))
                    continue
                # 空间角色继承
                if (
                    space_role is not None
                    and grant.principal_type == PrincipalType.SPACE_ROLE.value
                    and grant.principal_id == str(knowledge.space_id)
                    and grant.principal_role == space_role
                ):
                    merged_roles.append(ResourceRole(grant.resource_role))
            result[knowledge.id] = self.get_highest_role(merged_roles)
        return result

    def resolve_effective_role(
        self,
        *,
        user_id: int | None,
        resource_type: ResourceType,
        resource_id: str,
        team_id: str | None,
        space_id: str,
        is_public: bool,
    ) -> ResourceRole | None:
        """计算用户对一个知识库的最终资源角色。"""
        # 获取当前资源的所有授权
        grants = self.grant_repository.list_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
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
            if team_member is not None:
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
            if space_member is not None:
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
            is_public=(knowledge.visibility == KnowledgeVisibility.PUBLIC.value),
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
            is_public=document.is_public,
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
        """更新/创建授权
        1、已存在授权直接更新，接受最后提交生效（修改目前没加乐观锁）
        2、不存在则创建新的授权
        3、并发授权相同主体时，由数据库唯一性拦截
        4、并发冲突返回409，不修改另一个事务创建的授权

        """

        self._validate_principal_role(principal_type, principal_role)
        principal_id_value = str(principal_id)
        grant = self.grant_repository.get_by_principal(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id_value,
            principal_role=principal_role,
            for_update=True,
        )
        if resource_role == ResourceRole.NONE:
            if grant is not None:
                self.grant_repository.delete(grant)
                self.grant_repository.flush()
            return None

        if grant is None:
            # 这里在新增的时候增加了冲突处理
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
            # 增加冲突处理
            try:
                with self.db.begin_nested():
                    self.grant_repository.add(grant)
                    self.grant_repository.flush()
            except IntegrityError as exc:
                if is_duplicate_on(exc, self.GRANT_UNIQUE_CONSTRAINT):
                    raise HTTPException(
                        status_code=409,
                        detail="该主体的授权已被其他操作创建，请刷新后重试",
                    )
                raise

        else:
            grant.resource_role = resource_role.value
            grant.source = source.value
            grant.created_by = created_by
            self.grant_repository.flush()
        # 这里不commit
        return grant

    def create_creator_grant(
        self, *, knowledge: Knowledge, creator_id: int
    ) -> ResourceGrant:
        """创建创建者授权"""
        grant = self.upsert_grant(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            principal_type=PrincipalType.USER,
            principal_id=creator_id,
            principal_role=PrincipalRole.NONE,
            resource_role=ResourceRole.ADMIN,
            source=GrantSource.CREATOR,
            created_by=creator_id,
        )
        if grant is None:
            raise RuntimeError(f"创建者默认授权不能为空")
        return grant

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
        grants: list[ResourceGrant] = []
        for principal_role, resource_role in mappings.items():
            grant = self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.TEAM_ROLE,
                principal_id=knowledge.team_id,
                principal_role=principal_role,
                resource_role=resource_role,
                source=GrantSource.DEFAULT_POLICY,
                created_by=created_by,
            )
            if grant is None:
                raise RuntimeError(f"团队管理员默认授权不能为空")
            grants.append(grant)
        return grants

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
    ) -> ResourceGrant:
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
            grants.append(
                self.create_space_member_visibility_grant(
                    knowledge=knowledge,
                    created_by=creator_id,
                )
            )
        return grants

    def delete_space_member_visibility_grant(self, *, knowledge: Knowledge) -> None:
        """删除空间成员授权"""
        self.grant_repository.delete_by_principal(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            principal_type=PrincipalType.SPACE_ROLE,
            principal_id=knowledge.space_id,
            principal_role=PrincipalRole.MEMBER,
        )

        self.grant_repository.flush()

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
        if old_visibility == new_visibility:
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
