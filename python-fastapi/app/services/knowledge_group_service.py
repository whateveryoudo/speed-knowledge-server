"""知识库分组服务"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.common.utils import next_order_index, prepare_insert_order_index
from app.models.document import Document
from app.models.knowledge_group import KnowledgeGroup
from app.models.knowledge_group_relation import KnowledgeGroupRelation
from app.services.permission_service import PermissionService
from app.repositories.document_repository import DocumentRepository
from app.schemas.knowledge import KnowledgeResponse
from app.schemas.knowledge_group import (
    KnowledgeGroupCreate,
    KnowledgeGroupUpdateBody,
    KnowledgeGroupResponse,
    KnowledgeInGroupItem,
    DocumentSummaryItem,
    DEFAULT_DISPLAY_CONFIG,
)
from collections import defaultdict


class KnowledgeGroupService:
    """知识库分组服务"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.permission_service = PermissionService(db)
        self.document_repository = DocumentRepository(db)

    def _query(self):
        return self.db.query(KnowledgeGroup)

    def _get_owned_group(self, group_id: str, user_id: int) -> KnowledgeGroup:
        group = (
            self._query()
            .filter(KnowledgeGroup.id == group_id, KnowledgeGroup.user_id == user_id)
            .first()
        )
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库分组不存在"
            )
        return group

    def get_default_group(self, user_id: int) -> KnowledgeGroup:
        group = (
            self._query()
            .filter(
                KnowledgeGroup.user_id == user_id,
                KnowledgeGroup.is_default.is_(True),
            )
            .first()
        )
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="默认分组不存在"
            )
        return group

    def create(self, knowledge_group_in: KnowledgeGroupCreate) -> KnowledgeGroup:
        """创建知识库分组"""
        # 这里再头部插入
        order_index = prepare_insert_order_index(
            self.db, KnowledgeGroup, 0, user_id=knowledge_group_in.user_id
        )
        knowledge_group = KnowledgeGroup(
            user_id=knowledge_group_in.user_id,
            is_default=knowledge_group_in.is_default,
            group_name=knowledge_group_in.group_name,
            order_index=order_index,
            display_config=(
                knowledge_group_in.display_config or DEFAULT_DISPLAY_CONFIG
            ).model_dump(),
        )
        self.db.add(knowledge_group)
        self.db.commit()
        self.db.refresh(knowledge_group)
        return knowledge_group

    def get_list_by_user_id(self, user_id: int) -> List[KnowledgeGroup]:
        """获取知识库分组列表"""
        return (
            self._query()
            .filter(KnowledgeGroup.user_id == user_id)
            .order_by(KnowledgeGroup.order_index.asc(), KnowledgeGroup.created_at.asc())
            .all()
        )

    def _get_doc_order_type(self, group: KnowledgeGroup) -> int:
        """获取文档排序类型"""
        display_config = group.display_config or DEFAULT_DISPLAY_CONFIG.model_dump()
        if isinstance(display_config, dict):
            return display_config.get("doc_order_type", 1)
        return display_config.doc_order_type or 1

    def _build_doc_summaries(
        self,
        *,
        relations: List[KnowledgeGroupRelation],
        groups: List[KnowledgeGroup],
        readable_documents: List[Document],
        limit: int = 3,
    ) -> dict[str, List[DocumentSummaryItem]]:
        """使用最终可读文档构建每个知识库的TOP-N"""
        if not readable_documents:
            return {}

        group_by_id = {group.id: group for group in groups}

        order_type_by_knowledge_id: dict[str, int] = {}

        for relation in relations:
            group = group_by_id.get(relation.group_id)
            if group is None:
                continue
            order_type_by_knowledge_id[relation.knowledge_id] = (
                self._get_doc_order_type(group)
            )
        documents_by_knowledge_id: dict[str, List[Document]] = defaultdict(list)
        for document in readable_documents:
            documents_by_knowledge_id[document.knowledge_id].append(document)

        result: dict[str, List[DocumentSummaryItem]] = {}
        for knowledge_id, documents in documents_by_knowledge_id.items():
            order_type = order_type_by_knowledge_id.get(knowledge_id, 1)

            sorted_documents = sorted(
                documents,
                key=lambda x: (
                    (x.content_updated_at or x.updated_at)
                    if order_type == 1
                    else x.created_at
                ),
                reverse=True,
            )
            result[knowledge_id] = [
                DocumentSummaryItem(
                    id=document.id,
                    name=document.name,
                    slug=document.slug,
                    updated_at=document.updated_at,
                    content_updated_at=document.content_updated_at,
                )
                for document in sorted_documents[:limit]
            ]
        return result

    def get_list_with_knowledge(
        self, user_id: int, keyword: Optional[str] = None
    ) -> List[KnowledgeGroupResponse]:
        """获取带最终可读知识库和文档摘要的分组列表"""

        groups = self.get_list_by_user_id(user_id)
        keyword = (keyword or "").strip().lower()

        relations = (
            self.db.query(KnowledgeGroupRelation)
            .options(joinedload(KnowledgeGroupRelation.knowledge))
            .filter(KnowledgeGroupRelation.user_id == user_id)
            .order_by(
                KnowledgeGroupRelation.order_index.asc(),
                KnowledgeGroupRelation.created_at.asc(),
            )
            .all()
        )

        # 根据关键词缩小知识库的候选范围

        candidate_knowledge_ids: list[str] = list(
            dict.fromkeys(
                relation.knowledge_id
                for relation in relations
                if relation.knowledge is not None
                and (not keyword or keyword in (relation.knowledge.name or "").lower())
            )
        )

        # 同时完成知识库有效父链和read_book 的判断

        readable_knowledges = self.permission_service.list_readable_knowledges_by_ids(
            user_id=user_id,
            knowledge_ids=candidate_knowledge_ids,
        )
        readable_knowledge_by_id = {
            knowledge.id: knowledge for knowledge in readable_knowledges
        }

        readable_knowledge_ids = list(readable_knowledge_by_id.keys())

        candidate_documents = self.document_repository.list_active_by_knowledge_ids(
            readable_knowledge_ids,
        )

        # 进一步过滤 最终带有DOC_READ 的文档
        readable_documents = self.permission_service.filter_readable_documents(
            user_id=user_id,
            documents=candidate_documents,
        )

        documents_by_knowledge_id: dict[str, List[Document]] = defaultdict(list)

        for document in readable_documents:
            documents_by_knowledge_id[document.knowledge_id].append(document)

        document_counts = {
            knowledge_id: len(documents)
            for knowledge_id, documents in documents_by_knowledge_id.items()
        }
        document_summaries = self._build_doc_summaries(
            relations=relations,
            groups=groups,
            readable_documents=readable_documents,
            limit=3,
        )
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=user_id,
                knowledge_ids=readable_knowledge_ids,
            )
        )
        items_by_group: dict[str, List[KnowledgeInGroupItem]] = {
            group.id: [] for group in groups
        }
        for relation in relations:
            knowledge = readable_knowledge_by_id.get(relation.knowledge_id)
            if knowledge is None:
                continue
            from app.services.knowledge_service import KnowledgeService

            knowledge_response = KnowledgeResponse.model_validate(knowledge).model_copy(
                update={
                    "ability": ability_map.get(knowledge.id, {}),
                    "items_count": document_counts.get(knowledge.id, 0),
                    "scope_slug": KnowledgeService(self.db)._resolve_scope_slug(knowledge),
                }
            )
            group_item = KnowledgeInGroupItem(
                **knowledge_response.model_dump(),
                order_index=relation.order_index,
                relation_id=relation.id,
                doc_summary=document_summaries.get(knowledge.id, []),
            )
            items_by_group.setdefault(relation.group_id, []).append(group_item)
        return [
            KnowledgeGroupResponse(
                id=group.id,
                user_id=group.user_id,
                group_name=group.group_name,
                order_index=group.order_index,
                is_default=group.is_default,
                display_config=(
                    group.display_config or DEFAULT_DISPLAY_CONFIG.model_dump()
                ),
                created_at=group.created_at,
                updated_at=group.updated_at,
                knowledge_group_items=items_by_group.get(group.id, []),
            )
            for group in groups
        ]

    def update(
        self,
        group_id: str,
        user_id: int,
        knowledge_group_in: KnowledgeGroupUpdateBody,
    ) -> KnowledgeGroup:
        """更新知识库分组"""
        knowledge_group = self._get_owned_group(group_id, user_id)
        if knowledge_group_in.group_name is not None:
            knowledge_group.group_name = knowledge_group_in.group_name
        if knowledge_group_in.order_index is not None:
            knowledge_group.order_index = knowledge_group_in.order_index
        if knowledge_group_in.display_config is not None:
            knowledge_group.display_config = (
                knowledge_group_in.display_config.model_dump()
            )
        self.db.commit()
        self.db.refresh(knowledge_group)
        return knowledge_group

    def change_order_index(self, group_id: str, user_id: int, order_index: int) -> bool:
        """拖拽调整分组排序"""
        move_record = self._get_owned_group(group_id, user_id)
        old_index = move_record.order_index
        if old_index == order_index:
            return True

        if old_index < order_index:
            self.db.query(KnowledgeGroup).filter(
                KnowledgeGroup.user_id == user_id,
                KnowledgeGroup.order_index > old_index,
                KnowledgeGroup.order_index <= order_index,
            ).update(
                {KnowledgeGroup.order_index: KnowledgeGroup.order_index - 1},
                synchronize_session=False,
            )
        else:
            self.db.query(KnowledgeGroup).filter(
                KnowledgeGroup.user_id == user_id,
                KnowledgeGroup.order_index < old_index,
                KnowledgeGroup.order_index >= order_index,
            ).update(
                {KnowledgeGroup.order_index: KnowledgeGroup.order_index + 1},
                synchronize_session=False,
            )

        move_record.order_index = order_index
        self.db.commit()
        return True

    def delete(self, group_id: str, user_id: int) -> bool:
        """删除分组，知识库移动到默认分组"""
        group = self._get_owned_group(group_id, user_id)
        if group.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="默认分组不能删除",
            )

        default_group = self.get_default_group(user_id)
        relations = (
            self.db.query(KnowledgeGroupRelation)
            .filter(
                KnowledgeGroupRelation.user_id == user_id,
                KnowledgeGroupRelation.group_id == group_id,
            )
            .order_by(
                KnowledgeGroupRelation.order_index.asc(),
                KnowledgeGroupRelation.created_at.asc(),
            )
            .all()
        )

        for relation in relations:
            relation.group_id = default_group.id
            relation.order_index = next_order_index(
                self.db,
                KnowledgeGroupRelation,
                user_id=user_id,
                group_id=default_group.id,
            )
            self.db.flush()

        self.db.delete(group)
        self.db.commit()
        return True
