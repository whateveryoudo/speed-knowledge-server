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
    TeamMemberRole,
    SpaceMemberRole,
    DocumentVisibility,
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
        PrincipalType.SPACE: {
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

    @staticmethod
    def assert_assignable_role(
        *, resource_type: ResourceType, resource_role: ResourceRole
    ) -> None:
        """校验用户操作允许授权的资源角色"""
        if resource_type not in (ResourceType.KNOWLEDGE, ResourceType.DOCUMENT):
            raise HTTPException(status_code=422, detail="不支持的授权资源类型")
        if resource_role == ResourceRole.NONE:
            raise HTTPException(status_code=422, detail="资源角色不能为none")
        if resource_type == ResourceType.DOCUMENT and resource_role not in (
            ResourceRole.EDIT,
            ResourceRole.READ,
        ):
            raise HTTPException(
                status_code=422, detail="单篇文档授权仅支持可阅读或可编辑角色"
            )

    def _build_user_principals(
        self, user_id: int
    ) -> list[tuple[PrincipalType, int | str, PrincipalRole]]:
        """构建用户可用于匹配所有授权的主体列表"""
        principals: list[tuple[PrincipalType, int | str, PrincipalRole]] = [
            (PrincipalType.USER, user_id, PrincipalRole.NONE),
        ]
        team_members = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.user_id == user_id,
            )
            .all()
        )

        principals.extend(
            [
                (
                    PrincipalType.TEAM_ROLE,
                    team_member.team_id,
                    PrincipalRole(team_member.role),
                )
                for team_member in team_members
            ]
        )
        space_members = (
            self.db.query(SpaceMember)
            .filter(
                SpaceMember.user_id == user_id,
            )
            .all()
        )
        for space_member in space_members:
            space_role = SpaceMemberRole(space_member.role)
            # 公共区
            principals.append(
                (
                    PrincipalType.SPACE_ROLE,
                    space_member.space_id,
                    PrincipalRole(space_role.value),
                )
            )
            # 团队“空间所有成员可访问”按照空间内部成员整体匹配
            if space_role != SpaceMemberRole.EXTERNAL:
                principals.append(
                    (
                        PrincipalType.SPACE,
                        space_member.space_id,
                        PrincipalRole.NONE,
                    )
                )

        return principals

    def get_highest_role(self, roles: list[ResourceRole]) -> ResourceRole | None:
        """获取最高角色"""
        if not roles:
            return None
        return max(roles, key=lambda x: self.ROLE_PRIORITY[x])

    @staticmethod
    def _is_visibility_scope_grant(grant: ResourceGrant) -> bool:
        """判断是否是普通成员的可见范围入口，不包含SPACE_ROLE + owner/admin授权"""
        return (
            grant.principal_type == PrincipalType.SPACE.value
            and grant.principal_role == PrincipalRole.NONE.value
        ) or (
            grant.principal_type == PrincipalType.SPACE_ROLE.value
            and grant.principal_role
            in ((PrincipalRole.MEMBER.value, PrincipalRole.EXTERNAL.value))
        )

    def list_user_accessible_knowledge_ids(self, *, user_id: int) -> list[str]:
        """获取用户通过直接、团队、空间授权命中的知识库id"""
        principals = self._build_user_principals(user_id)
        return self.grant_repository.list_resource_ids_by_principals(
            resource_type=ResourceType.KNOWLEDGE, principals=principals
        )

    def list_user_granted_document_ids(self, *, user_id: int) -> list[str]:
        """获取用户授权命中的文档id"""
        principals = self._build_user_principals(user_id)
        return self.grant_repository.list_resource_ids_by_principals(
            resource_type=ResourceType.DOCUMENT, principals=principals
        )

    def _ensure_role_readable(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        principal_type: PrincipalType,
        principal_id: str,
        principal_role: PrincipalRole,
        created_by: int,
    ) -> None:
        """确保用户对资源有可读权限"""
        grant = self.grant_repository.get_by_principal(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
            principal_role=principal_role,
            for_update=True,
        )
        if grant is not None:
            return
        self.upsert_grant(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=principal_type,
            principal_id=principal_id,
            principal_role=principal_role,
            resource_role=ResourceRole.READ,
            source=GrantSource.DEFAULT_POLICY,
            created_by=created_by,
        )

    def _sync_team_space_visibility_grant(
        self,
        *,
        knowledge: Knowledge,
        old_visibility: KnowledgeVisibility,
        new_visibility: KnowledgeVisibility,
        operator_id: int,
    ):
        """团队下的授权范围切换"""
        if old_visibility == KnowledgeVisibility.SPACE:
            self.grant_repository.delete_by_principal(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.SPACE,
                principal_id=knowledge.space_id,
                principal_role=PrincipalRole.NONE,
            )
        if new_visibility == KnowledgeVisibility.SPACE:
            grant = self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.SPACE,
                principal_id=knowledge.space_id,
                principal_role=PrincipalRole.NONE,
                resource_role=ResourceRole.READ,
                source=GrantSource.VISIBILITY_POLICY,
                created_by=operator_id,
            )
            if grant is None:
                raise RuntimeError(f"团队知识库空间可见授权失败")

    def _sync_public_space_visibility_grant(
        self,
        *,
        knowledge: Knowledge,
        old_visibility: KnowledgeVisibility,
        new_visibility: KnowledgeVisibility,
        operator_id: int,
    ):
        """公共区下的授权范围切换"""
        # space->visible/private,需要移除成员和外部授权
        if old_visibility == KnowledgeVisibility.SPACE:
            for principal_role in (PrincipalRole.MEMBER, PrincipalRole.EXTERNAL):
                self.grant_repository.delete_by_principal(
                    resource_type=ResourceType.KNOWLEDGE,
                    resource_id=knowledge.id,
                    principal_type=PrincipalType.SPACE_ROLE,
                    principal_id=knowledge.space_id,
                    principal_role=principal_role,
                )
        # visible/private -> space,需要添加成员授权,外部联系人默认无授权
        if new_visibility == KnowledgeVisibility.SPACE:
            grant = self.upsert_grant(
                resource_type=ResourceType.KNOWLEDGE,
                resource_id=knowledge.id,
                principal_type=PrincipalType.SPACE_ROLE,
                principal_id=knowledge.space_id,
                principal_role=PrincipalRole.MEMBER,
                resource_role=ResourceRole.READ,
                source=GrantSource.VISIBILITY_POLICY,
                created_by=operator_id,
            )
            if grant is None:
                raise RuntimeError(f"公共区知识库空间成员可见授权失败")

    def sync_knowledge_visibility_policy_grants(
        self,
        *,
        knowledge: Knowledge,
        old_visibility: KnowledgeVisibility,
        new_visibility: KnowledgeVisibility,
        operator_id: int,
    ) -> None:
        """同步知识库visiblity对应的系统授权"""
        if (
            old_visibility == new_visibility
            or knowledge.space.type != SpaceType.ORGANIZATION
        ):
            return
        if knowledge.team_id is not None:
            self._sync_team_space_visibility_grant(
                knowledge=knowledge,
                old_visibility=old_visibility,
                new_visibility=new_visibility,
                operator_id=operator_id,
            )
            return
        self._sync_public_space_visibility_grant(
            knowledge=knowledge,
            old_visibility=old_visibility,
            new_visibility=new_visibility,
            operator_id=operator_id,
        )

    def sync_document_visibility_policy_grants(
        self,
        *,
        document: Document,
        old_visibility: DocumentVisibility,
        new_visibility: DocumentVisibility,
        operator_id: int,
    ) -> None:
        """同步文档可见授权"""
        knowledge = document.knowledge
        if knowledge is None:
            return
        if (
            old_visibility == new_visibility
            or knowledge.space.type != SpaceType.ORGANIZATION
        ):
            return
        if old_visibility == DocumentVisibility.SPACE:
            self.grant_repository.delete_by_principal(
                resource_type=ResourceType.DOCUMENT,
                resource_id=document.id,
                principal_type=PrincipalType.SPACE,
                principal_id=knowledge.space_id,
                principal_role=PrincipalRole.NONE,
            )
        if new_visibility == DocumentVisibility.SPACE:
            grant = self.upsert_grant(
                resource_type=ResourceType.DOCUMENT,
                resource_id=document.id,
                principal_type=PrincipalType.SPACE,
                principal_id=knowledge.space_id,
                principal_role=PrincipalRole.NONE,
                resource_role=ResourceRole.READ,
                source=GrantSource.VISIBILITY_POLICY,
                created_by=operator_id,
            )
            if grant is None:
                raise RuntimeError(f"文档空间可见授权失败")

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
        # 内部空间id列表（排除EXTERNAL）
        internal_space_ids = {
            member.space_id
            for member in space_members
            if member.role != SpaceMemberRole.EXTERNAL
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
                # 全员继承（内部空间）
                if (
                    knowledge.space_id in internal_space_ids
                    and grant.principal_type == PrincipalType.SPACE.value
                    and grant.principal_id == str(knowledge.space_id)
                    and grant.principal_role == PrincipalRole.NONE.value
                ):
                    merged_roles.append(ResourceRole(grant.resource_role))
                    continue
                # 空间角色继承（具体空间角色）
                if (
                    space_role is not None
                    and grant.principal_type == PrincipalType.SPACE_ROLE.value
                    and grant.principal_id == str(knowledge.space_id)
                    and grant.principal_role == space_role
                ):
                    merged_roles.append(ResourceRole(grant.resource_role))
                    continue
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
        include_visibility_scope: bool = True,
    ) -> ResourceRole | None:
        """计算用户对资源的最终资源角色。"""
        # 获取当前资源的所有授权
        grants = self.grant_repository.list_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
        )
        if not include_visibility_scope:
            grants = [
                grant for grant in grants if not self._is_visibility_scope_grant(grant)
            ]
        matched_grants: list[ResourceRole] = []
        # 计算最终角色
        if is_public and include_visibility_scope:
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

        # 空间继承(需要多找一个整体授权的)
        space_role_grants = [
            grant
            for grant in grants
            if grant.principal_type
            in (PrincipalType.SPACE_ROLE.value, PrincipalType.SPACE.value)
            and grant.principal_id == str(space_id)
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
                space_member_role = SpaceMemberRole(space_member.role)
                for grant in space_role_grants:
                    # 团队知识库的“空间内部成员整体”系统授权
                    if (
                        grant.principal_type == PrincipalType.SPACE.value
                        and grant.principal_role == PrincipalRole.NONE.value
                        and space_member_role != SpaceMemberRole.EXTERNAL
                    ):
                        matched_grants.append(ResourceRole(grant.resource_role))
                        continue
                    # 公共区按具体空间角色匹配。
                    if (
                        grant.principal_type == PrincipalType.SPACE_ROLE.value
                        and grant.principal_role == space_member_role.value
                    ):
                        matched_grants.append(ResourceRole(grant.resource_role))
        return self.get_highest_role(matched_grants)

    def resolve_granted_knowledge_role(
        self,
        *,
        user_id: int | None,
        knowledge: Knowledge,
        include_visibility_scope: bool = True,
    ) -> ResourceRole | None:
        """计算用户对一个知识库的最终资源角色。"""
        return self.resolve_effective_role(
            user_id=user_id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
            team_id=knowledge.team_id,
            space_id=knowledge.space_id,
            is_public=(knowledge.visibility == KnowledgeVisibility.PUBLIC.value),
            include_visibility_scope=include_visibility_scope,
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
            is_public=document.visibility == DocumentVisibility.PUBLIC.value,
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

    def create_knowledge_team_grant(
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
    def create_knowledge_space_admin_grant(
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
                self.create_knowledge_team_grant(
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
            self.create_knowledge_space_admin_grant(
                knowledge=knowledge,
                created_by=creator_id,
            )
        )
        return grants

    def delete_resource_grants(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> int:
        """删除资源授权"""
        delete_count = self.grant_repository.delete_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
        )
        self.grant_repository.flush()
        return delete_count

    def delete_direct_user_grant(
        self, *, resource_type: ResourceType, resource_id: str, user_id: int
    ) -> int:
        """删除直接用户授权"""
        return self.grant_repository.delete_by_principal(
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=PrincipalType.USER,
            principal_id=str(user_id),
            principal_role=PrincipalRole.NONE,
        )

    def list_document_context_user_ids(self, *, document: Document) -> list[int]:
        """获取当前可访问文档的已知用户ID,用于文档的@功能"""
        knowledge = document.knowledge
        if knowledge is None:
            return []
        document_grants = self.grant_repository.list_by_resource(
            resource_type=ResourceType.DOCUMENT,
            resource_id=document.id,
        )
        knowledge_grants = self.grant_repository.list_by_resource(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
        )
        if document.visibility != DocumentVisibility.INHERIT.value:
            knowledge_grants = [
                grant
                for grant in knowledge_grants
                if not self._is_visibility_scope_grant(grant)
            ]
        grants = document_grants + knowledge_grants
        user_ids: set[int] = set()
        team_roles: set[TeamMemberRole] = set()
        space_roles: set[SpaceMemberRole] = set()
        has_internal_space_grant = False
        for grant in grants:
            if (
                grant.principal_type == PrincipalType.USER.value
                and grant.principal_role == PrincipalRole.NONE.value
            ):
                user_ids.add(int(grant.principal_id))
                continue
            if (
                grant.principal_type == PrincipalType.TEAM_ROLE.value
                and knowledge.team_id is not None
                and grant.principal_id == str(knowledge.team_id)
            ):
                team_roles.add(TeamMemberRole(grant.principal_role))
                continue
            # 空间内部成员整体授权（owner/admin/member，不含 external）
            if (
                grant.principal_type == PrincipalType.SPACE.value
                and grant.principal_id == str(knowledge.space_id)
                and grant.principal_role == PrincipalRole.NONE.value
            ):
                has_internal_space_grant = True
                continue
            if (
                grant.principal_type == PrincipalType.SPACE_ROLE.value
                and grant.principal_id == str(knowledge.space_id)
            ):
                space_roles.add(SpaceMemberRole(grant.principal_role))
                continue

        if team_roles:
            team_rows = (
                self.db.query(TeamMember.user_id)
                .filter(
                    TeamMember.team_id == knowledge.team_id,
                    TeamMember.role.in_(team_roles),
                )
                .all()
            )
            user_ids.update(user_id for (user_id,) in team_rows)
        if space_roles:
            space_rows = (
                self.db.query(SpaceMember.user_id)
                .filter(
                    SpaceMember.space_id == knowledge.space_id,
                    SpaceMember.role.in_(space_roles),
                )
                .all()
            )
            user_ids.update(user_id for (user_id,) in space_rows)
        # 团队下的空间角色的集体授权
        if has_internal_space_grant:
            space_rows = (
                self.db.query(SpaceMember.user_id)
                .filter(
                    SpaceMember.space_id == knowledge.space_id,
                    SpaceMember.role.in_(
                        (
                            SpaceMemberRole.MEMBER,
                            SpaceMemberRole.ADMIN,
                            SpaceMemberRole.OWNER,
                        )
                    ),
                )
                .all()
            )
            user_ids.update(user_id for (user_id,) in space_rows)
        return list(user_ids)
