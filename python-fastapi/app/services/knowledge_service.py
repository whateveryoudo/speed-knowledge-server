"""知识库服务"""

from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge
from sqlalchemy import or_
from sqlalchemy.orm import Query
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.services.permission_service import PermissionService
from app.common.enums import (
    ResourceRole,
    ResourceType,
    resource_role_name,
    SpaceType,
    SpaceMemberRole,
    KnowledgeScopeType,
    KnowledgeVisibility,
    TeamMemberRole,
    PermissionScopeType,
    KnowledgeFromWay,
)
from typing import List, Optional
import secrets
import string
from datetime import datetime
from app.services.base_service import BaseService
from app.schemas.knowledge import (
    KnowledgeResponse,
    KnowledgeRouteContext,
    KnowledgeListQuery,
    KnowledgeListMineQuery,
)
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import joinedload
from app.schemas.query import SortRule, BaseSortOrder
from app.schemas.response import PaginationQuery, PaginationResponse
from app.common.pagination import paginate_after_fetch, paginate_response
from sqlalchemy.exc import IntegrityError
from app.common.utils import is_duplicate_entry, is_slug_duplicate
from app.services.knowledge_group_relation_service import KnowledgeGroupRelationService
from app.schemas.knowledge_group_relation import KnowledgeGroupRelationCreate
from app.services.knowledge_common_pin_service import KnowledgeCommonPinService
from app.common.enums import KnowledgeAbility, DocumentAbility
from app.services.document_service import DocumentService
from typing import Union
from app.services.resource_grant_service import ResourceGrantService
from app.models.space import Space
from app.models.space_member import SpaceMember
from app.models.team import Team
from app.models.team_member import TeamMember
from app.models.document import Document
from app.repositories.knowledge_repository import KnowledgeRepository

alphabet = string.ascii_letters + string.digits


class KnowledgeService(BaseService[Knowledge]):
    """知识库服务"""

    DEFAULT_KNOWLEDGE_SORTS = [
        SortRule(field="created_at", order=BaseSortOrder.DESC),
    ]

    SORT_COLUMN_MAP = {
        "created_at": Knowledge.created_at,
        "updated_at": Knowledge.updated_at,
        "content_updated_at": Knowledge.content_updated_at,
        "name": Knowledge.name,
    }

    def __init__(self, db: Session) -> None:
        super().__init__(db, Knowledge)
        self.permission_service = PermissionService(db)
        self.knowledge_repository = KnowledgeRepository(db)
        self.knowledge_group_relation_service = KnowledgeGroupRelationService(db)
        self.document_service = DocumentService(db)
        self.resource_grant_service = ResourceGrantService(db)

    def _validate_knowledge_container_access(
        self,
        *,
        creator_id: int,
        space_id: str,
        team_id: Optional[str],
    ) -> Space:
        """验证知识库容器(会有拦截判断)"""
        space = self.db.query(Space).filter(Space.id == space_id).first()
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在"
            )
        if space.type == SpaceType.PERSONAL:
            if space.owner_id != creator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问个人空间"
                )
            if team_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="个人空间不能归属团队",
                )
            return space
        space_member = (
            self.db.query(SpaceMember)
            .filter(SpaceMember.space_id == space_id, SpaceMember.user_id == creator_id)
            .first()
        )
        if not space_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="不是空间成员"
            )
        if team_id is None:
            if space_member.role == SpaceMemberRole.EXTERNAL:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="外部联系人不能在公共区创建知识库",
                )
            return space
        team = (
            self.db.query(Team)
            .filter(Team.id == team_id, Team.space_id == space_id)
            .first()
        )
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="团队不存在或不属于当前空间",
            )
        team_member = (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == creator_id)
            .first()
        )
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="不是团队成员"
            )
        if team_member.role == TeamMemberRole.READONLY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="团队只读成员不能创建知识库",
            )
        return space

    def to_wrap_knowledge_response_for_guest(
        self, knowledge: Knowledge
    ) -> KnowledgeResponse:
        """包装知识库响应(游客访问)"""
        ability = self.permission_service.get_guest_readonly_abilities()
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={"ability": ability}
        )

    def to_wrap_knowledge_response(
        self, knowledge: Knowledge, user_id: int
    ) -> KnowledgeResponse:
        """包装知识库响应(追加一些其他参数)"""
        ability = self.permission_service.get_effective_abilities(
            user_id=user_id,
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge.id,
        )
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={
                "ability": ability,
            }
        )

    def _generate_slug(self) -> str:
        """生成知识库短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def create(self, knowledge_in: KnowledgeCreate) -> Knowledge:
        """创建知识库"""
        if knowledge_in.creator_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id is required"
            )
        # 获取space空间
        space = self._validate_knowledge_container_access(
            creator_id=knowledge_in.creator_id,
            space_id=knowledge_in.space_id,
            team_id=knowledge_in.team_id,
        )

        last_exec: IntegrityError | None = None
        for _ in range(3):
            try:
                temp_slug = self._generate_slug()
                while self.knowledge_repository.exists_slug(temp_slug):
                    temp_slug = self._generate_slug()
                knowledge = Knowledge(
                    creator_id=knowledge_in.creator_id,
                    name=knowledge_in.name,
                    team_id=knowledge_in.team_id,
                    icon=knowledge_in.icon,
                    slug=temp_slug,
                    space_id=space.id,
                    description=knowledge_in.description,
                )
                self.db.add(knowledge)
                self.db.flush()
                # 插入授权
                self.resource_grant_service.create_default_knowledge_grants(
                    knowledge=knowledge,
                    creator_id=knowledge_in.creator_id,
                )
                group_id = knowledge_in.group_id
                if not group_id:
                    from app.services.knowledge_group_service import (
                        KnowledgeGroupService,
                    )

                    default_group = KnowledgeGroupService(self.db).get_default_group(
                        knowledge_in.creator_id
                    )
                    group_id = default_group.id
                self.knowledge_group_relation_service.create(
                    KnowledgeGroupRelationCreate(
                        user_id=knowledge_in.creator_id,
                        knowledge_id=knowledge.id,
                        group_id=group_id,
                    ),
                    commit=False,
                )
                # 创建默认权限组(追加3个角色权限,这里选取3个类别，NONE不追加)
                for role in (
                    ResourceRole.READ,
                    ResourceRole.EDIT,
                    ResourceRole.ADMIN,
                ):
                    permission_group_service = PermissionGroupService(self.db)
                    permission_group_service.create_permission_group(
                        # 权限组名称: 知识库名称(知识库短链)-角色名称
                        PermissionGroupCreate(
                            name=f"{knowledge.name}({knowledge.slug})-{resource_role_name[role.value]}",
                            role_key=role.value,
                            scope_type=PermissionScopeType.KNOWLEDGE,
                            scope_id=knowledge.id,
                        )
                    )
                # 默认添加为常用知识库
                common_pin_service = KnowledgeCommonPinService(self.db)
                common_pin_service.create(
                    knowledge_id=knowledge.id, creator_id=knowledge_in.creator_id, commit=False
                )

                self.db.commit()
                self.db.refresh(knowledge)
                return knowledge
            except IntegrityError as e:
                self.db.rollback()
                last_exec = e
                if is_slug_duplicate(e, "slug"):
                    continue
                if is_duplicate_entry(e):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="知识库分组关系已存在",
                    )
                raise e
        if last_exec:
            raise last_exec

    def create_knowledge_for_quick_document(self, data: KnowledgeCreate) -> Knowledge:
        """创建默认知识库(这里不再走统一创建默认团队的逻辑)"""
        if data.creator_id is None:
            raise ValueError("create_id is required")
        # 这里不默认创建团队
        # if not data.team_id:

        #     # 前端未传入team_id
        #     from app.services.team_service import TeamService

        #     team_service = TeamService(self.db)
        #     default_team = team_service.get_default_team(data.user_id, data.space_id)
        #     if not default_team:
        #         raise HTTPException(
        #             status_code=status.HTTP_404_NOT_FOUND, detail="默认团队不存在"
        #         )
        #     default_team_id = default_team.id
        # else:
        #     default_team_id = data.team_id
        # 查找当前用户空间下是否存在知识库
        knowledge = (
            self.get_active_query()
            .filter(
                Knowledge.creator_id == data.creator_id,
                Knowledge.space_id == data.space_id,
                Knowledge.team_id.is_(None),
            )
            .first()
        )
        if knowledge:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="已有知识库，请选择知识库进行文档创建",
            )
        return self.create(data.model_copy(update={"team_id": None}))

    def _validate_visibility(
        self, *, knowledge: Knowledge, visibility: KnowledgeVisibility
    ) -> None:
        """空间模式仅支持空间成员可见"""
        if (
            visibility == KnowledgeVisibility.SPACE
            and knowledge.space.type != SpaceType.ORGANIZATION
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="个人空间不能设置为空间成员可见",
            )

    def update_visibility(
        self, *, knowledge: Knowledge, visibility: KnowledgeVisibility, operator_id: int
    ) -> bool:
        """更新可见范围"""
        self._validate_visibility(knowledge=knowledge, visibility=visibility)
        old_visibility = KnowledgeVisibility(knowledge.visibility)
        if old_visibility == visibility:
            return True
        knowledge.visibility = visibility.value
        # 更新可见范围授权
        self.resource_grant_service.sync_knowledge_visibility_policy_grants(
            knowledge=knowledge,
            old_visibility=old_visibility,
            new_visibility=visibility,
            operator_id=operator_id,
        )
        self.db.commit()
        return True

    def _build_owned_query(self, *, user_id: int):
        """自己创建的知识库查询条件"""
        return self.knowledge_repository.active_list_query().filter(
            Knowledge.creator_id == user_id,
        )

    def _apply_sorter(self, query, sorts: List[SortRule]):
        """排序追加(这里是多维度排序)"""
        order_clauses = []
        if not sorts:
            sorts = self.DEFAULT_KNOWLEDGE_SORTS
        for rule in sorts:
            column = self.SORT_COLUMN_MAP.get(rule.field)
            if column is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的排序字段:{rule.field}",
                )
            if rule.order == BaseSortOrder.DESC:
                order_clauses.append(column.desc())
            else:
                order_clauses.append(column.asc())

        return query.order_by(*order_clauses)

    def _apply_abilities_filter(
        self,
        query,
        user_id: int,
        abilities: List[Union[KnowledgeAbility, DocumentAbility]] | None,
    ):
        """按照用户的最终能力筛选知识库"""
        if not abilities:
            return query
        candidate_rows = query.with_entities(Knowledge.id).all()
        candidate_ids = [knowledge_id for (knowledge_id,) in candidate_rows]
        if not candidate_ids:
            return query.filter(Knowledge.id.in_([]))
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=user_id, knowledge_ids=candidate_ids
            )
        )
        allowed_ids = [
            knowledge_id
            for knowledge_id in candidate_ids
            if all(
                ability_map.get(knowledge_id, {}).get(ability, False)
                for ability in abilities
            )
        ]
        return query.filter(Knowledge.id.in_(allowed_ids))

    def _apply_filters(
        self, query, query_in: KnowledgeListQuery | KnowledgeListMineQuery
    ):
        """筛选条件追加(可以处理更多参数)"""
        if query_in.keyword:
            keyword = query_in.keyword.strip()
            if keyword:
                query = query.filter(Knowledge.name.ilike(f"%{keyword}%"))
        return query

    def _build_mine_query(self, *, user_id: int):
        """用户创建或者通过其他授权参与的全部知识库"""
        accessible_ids = self.resource_grant_service.list_user_accessible_knowledge_ids(
            user_id=user_id
        )
        return self.knowledge_repository.active_list_query().filter(
            or_(
                Knowledge.creator_id == user_id,
                Knowledge.id.in_(accessible_ids),
            ),
        )

    def _build_collaboration_query(self, *, user_id: int):
        """用户通过直接、团队、空间授权参与的知识库"""
        accessible_ids = self.resource_grant_service.list_user_accessible_knowledge_ids(
            user_id=user_id
        )
        return self.knowledge_repository.active_list_query().filter(
            Knowledge.id.in_(accessible_ids), Knowledge.creator_id != user_id
        )

    def _paginate_readable_knowledge_query(
        self,
        *,
        query: Query,
        user_id: int,
        query_in: KnowledgeListQuery | KnowledgeListMineQuery,
    ) -> tuple[list[Knowledge], int, bool]:
        """过滤最终可读性，在进行内部过滤"""
        candidate_rows = query.all()
        readable_rows = self.permission_service.filter_readable_knowledges(
            user_id=user_id, knowledges=candidate_rows
        )
        pagination_query = PaginationQuery(
            page=query_in.page, page_size=query_in.page_size
        )
        page_rows = readable_rows[
            pagination_query.skip : pagination_query.skip + pagination_query.limit
        ]

        return paginate_after_fetch(
            items=page_rows, total=len(readable_rows), pagination_query=pagination_query
        )

    def _to_response(
        self,
        *,
        user_id: int,
        knowledge: Knowledge,
        ability_map: dict[str, dict],
    ) -> KnowledgeResponse:
        """转换为响应结构"""
        source = (
            KnowledgeFromWay.OWN
            if knowledge.creator_id == user_id
            else KnowledgeFromWay.COLLABORATION
        )
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={"ability": ability_map.get(knowledge.id, {}), "source": source}
        )

    def get_list_by_user_id(
        self, *, user_id: int, query_in: KnowledgeListQuery
    ) -> PaginationResponse:
        """分类查询知识库列表（个人/邀请协作）"""
        if query_in.scope == KnowledgeFromWay.OWN:
            query = self._build_owned_query(user_id=user_id)
        elif query_in.scope == KnowledgeFromWay.COLLABORATION:
            query = self._build_collaboration_query(user_id=user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="scope参数错误"
            )

        # 补全查询条件
        query = self._apply_filters(query, query_in)
        query = self._apply_sorter(query, query_in.sorts)

        rows, total, has_more = self._paginate_readable_knowledge_query(
            query=query, user_id=user_id, query_in=query_in
        )

        # 数据补充（权限）

        knowledge_ids = [knowledge.id for knowledge in rows]
        # 批量拿回权限能力
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=user_id, knowledge_ids=knowledge_ids
            )
        )

        items = [
            self._to_response(
                knowledge=knowledge,
                user_id=user_id,
                ability_map=ability_map,
            )
            for knowledge in rows
        ]

        return paginate_response(items, total, has_more, query_in)

    def get_list_mine(
        self, *, user_id: int, query_in: KnowledgeListMineQuery
    ) -> PaginationResponse:
        """获取我的知识库列表(主要是用于支持按照某些条件过滤)"""
        query = self._build_mine_query(user_id=user_id)
        query = self._apply_filters(query, query_in)
        query = self._apply_abilities_filter(
            query, user_id=user_id, abilities=query_in.abilities
        )
        query = self._apply_sorter(query, query_in.sorts)

        rows, total, has_more = self._paginate_readable_knowledge_query(
            query=query, user_id=user_id, query_in=query_in
        )

        # 数据补充（权限）
        knowledge_ids = [knowledge.id for knowledge in rows]
        # 批量拿回权限能力
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=user_id, knowledge_ids=knowledge_ids
            )
        )
        # 组装成和get_list_by_user_id一样的响应结构
        items = [
            self._to_response(
                knowledge=knowledge,
                user_id=user_id,
                ability_map=ability_map,
            )
            for knowledge in rows
        ]
        return paginate_response(items, total, has_more, query_in)

    def soft_delete(self, knowledge_id: str) -> bool:
        """软删除知识库(这里不会去软删除下方的文档，会在访问侧做权限判断)"""
        knowledge = self.get_active_query().filter(Knowledge.id == knowledge_id).first()
        if knowledge is None:
            return False
        knowledge.soft_delete()
        self.db.commit()
        return True

    def leave_direct_collaboration(self, *, knowledge_id: str, user_id: int) -> None:
        """移除用户对知识库的直接授权"""
        knowledge = self.knowledge_repository.get_active_by_id(knowledge_id)
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        if knowledge.creator_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不能移除自己的直接授权"
            )
        deleted_count = self.resource_grant_service.delete_direct_user_grant(
            resource_type=ResourceType.KNOWLEDGE,
            resource_id=knowledge_id,
            user_id=user_id,
        )
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="非直接授权，无法单独退出(可能来自团队/空间授权)",
            )

    def _resolve_scope_type(self, knowledge: Knowledge) -> KnowledgeScopeType:
        """获取知识库范围类型"""
        if knowledge.team_id is not None:
            return KnowledgeScopeType.TEAM
        elif knowledge.space.type == SpaceType.PERSONAL:
            return KnowledgeScopeType.PERSONAL
        else:
            return KnowledgeScopeType.SPACE

    def _resolve_scope_slug(self, knowledge: Knowledge) -> str:
        """获取知识库范围短链"""
        if knowledge.team_id is not None:
            if not knowledge.team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
                )
            return knowledge.team.slug
        elif knowledge.space.type == SpaceType.PERSONAL:
            if not knowledge.creator:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="无创建者用户名"
                )
            return knowledge.creator.username
        else:
            if not knowledge.space.public_area_slug:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="空间公共区域短链不存在",
                )
            return knowledge.space.public_area_slug

    def get_knowledge_route_context(self, knowledge_id: str) -> KnowledgeRouteContext:
        """获取文档路由上下文(主要是和当前文档访问相关)"""
        knowledge_full_info = (
            self.get_active_query()
            .filter(Knowledge.id == knowledge_id)
            .options(
                joinedload(Knowledge.creator),
                joinedload(Knowledge.team),
                joinedload(Knowledge.space),
            )
            .first()
        )
        if not knowledge_full_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        # 去掉必填判断
        # team = knowledge_full_info.team if knowledge_full_info else None
        # if not team:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
        #     )
        return KnowledgeRouteContext(
            knowledge_id=knowledge_full_info.id,
            knowledge_name=knowledge_full_info.name,
            knowledge_slug=knowledge_full_info.slug,
            scope_type=self._resolve_scope_type(knowledge_full_info),
            team_id=knowledge_full_info.team_id if knowledge_full_info.team else None,
            team_name=(
                knowledge_full_info.team.name if knowledge_full_info.team else None
            ),
            team_slug=(
                knowledge_full_info.team.slug if knowledge_full_info.team else None
            ),
            space_id=knowledge_full_info.space_id,
            space_domain=knowledge_full_info.space.domain,
            scope_slug=self._resolve_scope_slug(knowledge_full_info),
        )

    def get_knowledge_route_context_multiple(
        self, knowledge_ids: list[str]
    ) -> dict[str, KnowledgeRouteContext]:
        """批量获取知识库路由上下文"""
        knowledge_full_infos = (
            self.get_active_query()
            .filter(Knowledge.id.in_(knowledge_ids))
            .options(
                joinedload(Knowledge.creator),
                joinedload(Knowledge.team),
                joinedload(Knowledge.space),
            )
            .all()
        )
        return {
            knowledge_full_info.id: KnowledgeRouteContext(
                knowledge_id=knowledge_full_info.id,
                knowledge_name=knowledge_full_info.name,
                knowledge_slug=knowledge_full_info.slug,
                scope_type=self._resolve_scope_type(knowledge_full_info),
                team_id=(
                    knowledge_full_info.team_id if knowledge_full_info.team else None
                ),
                team_name=(
                    knowledge_full_info.team.name if knowledge_full_info.team else None
                ),
                team_slug=(
                    knowledge_full_info.team.slug if knowledge_full_info.team else None
                ),
                space_id=knowledge_full_info.space_id,
                space_domain=knowledge_full_info.space.domain,
                scope_slug=self._resolve_scope_slug(knowledge_full_info),
            )
            for knowledge_full_info in knowledge_full_infos
        }
