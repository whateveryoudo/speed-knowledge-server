"""知识库服务"""

from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge
from app.models.collaborator import Collaborator
from sqlalchemy import or_, and_, exists
from app.schemas.collaborator import CollaboratorCreate
from app.services.collaborator_service import CollaboratorService
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.models.document import Document
from app.services.permission_service import PermissionService
from app.common.enums import (
    CollaboratorRole,
    CollaborateResourceType,
    collaborator_role_name,
    CollaboratorStatus,
    KnowledgeFromWay,
    CollaboratorSource,
)
from typing import List, Optional, Dict
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
from app.common.pagination import paginate_query, paginate_response
from sqlalchemy.exc import IntegrityError
from app.common.utils import is_duplicate_entry, is_slug_duplicate
from app.services.knowledge_group_relation_service import KnowledgeGroupRelationService
from app.schemas.knowledge_group_relation import KnowledgeGroupRelationCreate
from app.services.knowledge_common_pin_service import KnowledgeCommonPinService
from app.models.permission_group import PermissionGroup
from app.models.permission_ability import PermissionAbility
from app.common.enums import KnowledgeAbility, DocumentAbility
from app.services.resource_access_service import ResourceAccessService
from app.services.document_service import DocumentService
from typing import Union

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

    def to_wrap_knowledge_response_for_guest(
        self, knowledge: Knowledge
    ) -> KnowledgeResponse:
        """包装知识库响应(游客访问)"""
        ability = self.permission_service.get_guest_readonly_abilities()
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={
                "ability": ability,
            }
        )

    def to_wrap_knowledge_response(
        self, knowledge: Knowledge, user_id: int
    ) -> KnowledgeResponse:
        """包装知识库响应(追加一些其他参数)"""
        ability = self.permission_service.get_permission_ability_by_resource(
            user_id, CollaborateResourceType.KNOWLEDGE, knowledge.id
        )
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={
                "ability": ability,
            }
        )

    def _generate_slug(self) -> str:
        """生成知识库短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def __init__(self, db: Session) -> None:
        super().__init__(db, Knowledge)
        self.permission_service = PermissionService(db)
        self.knowledge_group_relation_service = KnowledgeGroupRelationService(db)
        self.document_service = DocumentService(db)
    def create(self, knowledge_in: KnowledgeCreate) -> Knowledge:
        """创建知识库"""
        last_exec: IntegrityError | None = None
        for _ in range(3):
            try:
                temp_slug = self._generate_slug()
                while (
                    self.get_active_query().filter(Knowledge.slug == temp_slug).first()
                ):
                    temp_slug = self._generate_slug()
                # 默认isPublic为False
                knowledge = Knowledge(
                    user_id=knowledge_in.user_id,
                    name=knowledge_in.name,
                    team_id=knowledge_in.team_id,
                    icon=knowledge_in.icon,
                    slug=temp_slug,
                    space_id=knowledge_in.space_id,
                    description=knowledge_in.description,
                )
                self.db.add(knowledge)
                self.db.flush()
                group_id = knowledge_in.group_id
                if not group_id:
                    from app.services.knowledge_group_service import (
                        KnowledgeGroupService,
                    )

                    default_group = KnowledgeGroupService(self.db).get_default_group(
                        knowledge_in.user_id
                    )
                    group_id = default_group.id
                self.knowledge_group_relation_service.create(
                    KnowledgeGroupRelationCreate(
                        user_id=knowledge_in.user_id,
                        knowledge_id=knowledge.id,
                        group_id=group_id,
                    ),
                    commit=False,
                )
                # 追加默认协作者
                collaborator_service = CollaboratorService(self.db)
                collaborator_service.join_default_collaborator(
                    CollaboratorCreate(
                        user_id=knowledge_in.user_id,
                        knowledge_id=knowledge.id,
                        target_type=CollaborateResourceType.KNOWLEDGE,
                    )
                )
                # 创建默认权限组(追加3个角色权限)
                for role in CollaboratorRole:
                    permission_group_service = PermissionGroupService(self.db)
                    permission_group_service.create_permission_group(
                        # 权限组名称: 知识库名称(知识库短链)-角色名称
                        PermissionGroupCreate(
                            name=f"{knowledge.name}({knowledge.slug})-{collaborator_role_name[role.value]}",
                            role=role,
                            target_type=CollaborateResourceType.KNOWLEDGE,
                            target_id=knowledge.id,
                        )
                    )
                # 默认添加为常用知识库
                common_pin_service = KnowledgeCommonPinService(self.db)
                common_pin_service.create(
                    knowledge.id, knowledge_in.user_id, commit=False
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
        """创建默认知识库(目前提供给直接创建文档使用, 默认知识库的团队和空间是默认的)"""

        if not data.team_id:
            # 前端未传入team_id
            from app.services.team_service import TeamService

            team_service = TeamService(self.db)
            default_team = team_service.get_default_team(data.user_id, data.space_id)
            if not default_team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="默认团队不存在"
                )
            default_team_id = default_team.id
        else:
            default_team_id = data.team_id
        # 查找当前用户空间下是否存在知识库
        knowledge = (
            self.get_active_query()
            .filter(
                Knowledge.user_id == data.user_id,
                Knowledge.team_id == default_team_id,
                Knowledge.space_id == data.space_id,
                Knowledge.deleted_at.is_(None),
            )
            .first()
        )
        if knowledge:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="已有知识库，请选择知识库进行文档创建",
            )
        return self.create(data.model_copy(update={"team_id": default_team_id}))

    def get_by_id_or_slug(self, identifier: str) -> Knowledge:
        """通过知识库id/短链查询知识库(附带文档数量)"""
        knowledge = (
            self.get_active_query()
            .filter(
                or_(Knowledge.id == identifier, Knowledge.slug == identifier),
            )
            .first()
        )
        if knowledge:
            items_count = (
                self.db.query(Document)
                .filter(Document.knowledge_id == knowledge.id)
                .count()
            )
            knowledge.items_count = items_count
        return knowledge

    def _build_personal_query(self, query_in: KnowledgeListQuery):
        """个人知识库查询条件"""
        return (
            self.db.query(Collaborator)
            .join(Knowledge, Collaborator.knowledge_id == Knowledge.id)
            .filter(
                Collaborator.user_id == query_in.user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                Collaborator.target_type == CollaborateResourceType.KNOWLEDGE,
                Collaborator.source == CollaboratorSource.CREATOR.value,
                Knowledge.deleted_at.is_(None),
            )
            .options(joinedload(Collaborator.knowledge).joinedload(Knowledge.team))
        )

    def _apply_filters(self, query, query_in: KnowledgeListQuery):
        """筛选条件追加(可以处理更多参数)"""
        if query_in.keyword:
            keyword = query_in.keyword.strip()
            if keyword:
                query = query.filter(Knowledge.name.ilike(f"%{keyword}%"))
        return query

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
        self, query, abilities: List[Union[KnowledgeAbility, DocumentAbility]]
    ):
        """权限能力过滤"""
        if not abilities:
            return query

        for ability in abilities:
            ability_key = ability.value if hasattr(ability, "value") else ability
            query = query.filter(
                exists().where(
                    and_(
                        PermissionGroup.target_id == Knowledge.id,
                        PermissionGroup.target_type
                        == CollaborateResourceType.KNOWLEDGE.value,
                        PermissionGroup.role == Collaborator.role,
                        PermissionAbility.permission_group_id == PermissionGroup.id,
                        PermissionAbility.ability_key == ability_key,
                        PermissionAbility.enable.is_(True),
                    )
                )
            )
        return query

    def _build_mine_query(self, query_in: KnowledgeListMineQuery):
        """我的知识库查询条件"""
        return (
            self.db.query(Collaborator)
            .join(Knowledge, Collaborator.knowledge_id == Knowledge.id)
            .filter(
                Collaborator.user_id == query_in.user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                Collaborator.target_type == CollaborateResourceType.KNOWLEDGE,
                Knowledge.deleted_at.is_(None),
            )
            .options(joinedload(Collaborator.knowledge).joinedload(Knowledge.team))
        )

    def _build_collaborate_query(self, query_in: KnowledgeListQuery):
        """邀请协作知识库查询条件"""
        return (
            self.db.query(Collaborator)
            .join(Knowledge, Collaborator.knowledge_id == Knowledge.id)
            .filter(
                Collaborator.user_id == query_in.user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                Collaborator.target_type == CollaborateResourceType.KNOWLEDGE,
                Collaborator.source != CollaboratorSource.CREATOR.value,
                Knowledge.deleted_at.is_(None),
            )
            .options(joinedload(Collaborator.knowledge).joinedload(Knowledge.team))
        )

    def toggle_public(self, identifier: str) -> bool:
        """切换知识库公开状态"""
        knowledge = (
            self.get_active_query()
            .filter(
                or_(Knowledge.id == identifier, Knowledge.slug == identifier),
            )
            .first()
        )
        if knowledge:
            knowledge.is_public = not knowledge.is_public
            # 默认不开启高级密码保护
            self.db.commit()
            return True
        return False

    def _to_response(
        self,
        knowledge: Knowledge,
        collaborator_id: str,
        scope: KnowledgeFromWay,
        ability_map: Optional[Dict[str, Dict]] = None,
    ) -> KnowledgeResponse:
        """转换为响应结构"""
        return KnowledgeResponse.model_validate(knowledge).model_copy(
            update={
                "ability": ability_map.get(knowledge.id, {}),
                "source": scope,
                "collaborator_id": collaborator_id,
            }
        )

    def get_list_by_user_id(self, query_in: KnowledgeListQuery) -> PaginationResponse:
        """分类查询知识库列表（个人/邀请协作）"""
        if query_in.scope == KnowledgeFromWay.OWN or not query_in.scope:
            query = self._build_personal_query(query_in)
        elif query_in.scope == KnowledgeFromWay.COLLABORATION:
            query = self._build_collaborate_query(query_in)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="scope参数错误"
            )

        # 补全查询条件
        query = self._apply_filters(query, query_in)
        query = self._apply_sorter(query, query_in.sorts)

        rows, total, has_more = paginate_query(
            query, PaginationQuery(page=query_in.page, page_size=query_in.page_size)
        )

        # 数据补充（权限）

        knowledge_ids = [row.knowledge_id for row in rows]
        # 批量拿回权限能力
        ability_map = (
            self.permission_service.get_multiple_permission_ability_by_resources(
                query_in.user_id, CollaborateResourceType.KNOWLEDGE, knowledge_ids
            )
        )

        items = [
            self._to_response(row.knowledge, row.id, query_in.scope, ability_map)
            for row in rows
        ]

        return paginate_response(items, total, has_more, query_in)

    def get_list_mine(self, query_in: KnowledgeListMineQuery) -> PaginationResponse:
        """获取我的知识库列表(主要是用于支持按照某些条件过滤)"""
        query = self._build_mine_query(query_in)
        query = self._apply_abilities_filter(query, query_in.abilities)
        query = self._apply_filters(query, query_in)
        query = self._apply_sorter(query, query_in.sorts)

        rows, total, has_more = paginate_query(
            query, PaginationQuery(page=query_in.page, page_size=query_in.page_size)
        )

        # 数据补充（权限）
        knowledge_ids = [row.knowledge_id for row in rows]
        # 批量拿回权限能力
        ability_map = (
            self.permission_service.get_multiple_permission_ability_by_resources(
                query_in.user_id, CollaborateResourceType.KNOWLEDGE, knowledge_ids
            )
        )
        # 组装成和get_list_by_user_id一样的响应结构
        items = [
            self._to_response(
                row.knowledge,
                row.id,
                (
                    KnowledgeFromWay.OWN
                    if row.source == CollaboratorSource.CREATOR.value
                    else KnowledgeFromWay.COLLABORATION
                ),
                ability_map,
            )
            for row in rows
        ]
        return paginate_response(items, total, has_more, query_in)

    def soft_delete(self, knowledge_id: str) -> bool:
        """软删除知识库"""
        knowledge = self.get_active_query().filter(Knowledge.id == knowledge_id).first()
        if knowledge:
            knowledge.deleted_at = datetime.now()
            # 知识库下方文档都要软删除
            self.document_service.soft_muitiple_delete_by_knowledge_id(knowledge.id)
            self.db.commit()
            return True
        return False

    def get_knowledge_route_context(self, knowledge_id: str) -> KnowledgeRouteContext:
        """获取文档路由上下文(主要是和当前文档访问相关)"""
        knowledge_full_info = (
            self.get_active_query()
            .filter(Knowledge.id == knowledge_id)
            .first()
            .options(joinedload(Knowledge.team).joinedload(Knowledge.space))
            .first()
        )
        if not knowledge_full_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        team = knowledge_full_info.team if knowledge_full_info else None
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
            )
        return KnowledgeRouteContext(
            knowledge_id=knowledge_full_info.id,
            knowledge_name=knowledge_full_info.name,
            knowledge_slug=knowledge_full_info.slug,
            team_id=knowledge_full_info.team_id,
            team_name=knowledge_full_info.team.name,
            team_slug=knowledge_full_info.team.slug,
            space_id=knowledge_full_info.space_id,
            space_domain=knowledge_full_info.space.domain,
        )

    def get_knowledge_route_context_multiple(
        self, knowledge_ids: list[str]
    ) -> dict[str, KnowledgeRouteContext]:
        """批量获取知识库路由上下文"""
        knowledge_full_infos = (
            self.get_active_query()
            .filter(Knowledge.id.in_(knowledge_ids))
            .options(
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
                team_id=knowledge_full_info.team_id,
                team_name=knowledge_full_info.team.name,
                team_slug=knowledge_full_info.team.slug,
                space_id=knowledge_full_info.space_id,
                space_domain=knowledge_full_info.space.domain,
            )
            for knowledge_full_info in knowledge_full_infos
        }
