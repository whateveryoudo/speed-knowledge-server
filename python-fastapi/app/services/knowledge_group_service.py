"""知识库分组服务"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.common.utils import next_order_index
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.models.knowledge_group import KnowledgeGroup
from app.models.knowledge_group_relation import KnowledgeGroupRelation
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
        knowledge_group = KnowledgeGroup(
            user_id=knowledge_group_in.user_id,
            is_default=knowledge_group_in.is_default,
            group_name=knowledge_group_in.group_name,
            order_index=knowledge_group_in.order_index,
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
        relations: List[KnowledgeGroupRelation],
        groups: List[KnowledgeGroup],
        active_knowledge_ids: List[str],
        *,
        limit: int = 3,
    ) -> dict[str, List[DocumentSummaryItem]]:
        """批量获取文档top3"""
        if not active_knowledge_ids:
            return {}

        group_map = {group.id: group for group in groups}

        knowledge_order_type: dict[str, int] = {}

        for relation in relations:
            knowledge = relation.knowledge
            if not knowledge or knowledge.deleted_at is not None:
                continue
            if knowledge.id not in knowledge_order_type:
                group = group_map.get(relation.group_id)
                knowledge_order_type[knowledge.id] = (
                    self._get_doc_order_type(group) if group else 1
                )

        docs = (
            self.db.query(Document)
            .filter(
                Document.knowledge_id.in_(active_knowledge_ids),
                Document.deleted_at.is_(None),
            )
            .all()
        )
        docs_by_knowledge: dict[str, List[Document]] = defaultdict(list)
        for doc in docs:
            docs_by_knowledge[doc.knowledge_id].append(doc)
        doc_summaries: dict[str, List[DocumentSummaryItem]] = {}
        for knowledge_id, docs in docs_by_knowledge.items():
            order_type = knowledge_order_type.get(knowledge_id, 1)
            sorted_docs = sorted(
                docs,
                key=lambda x: (x.content_update_at or x.updated_at if order_type == 1 else x.created_at),
                reverse=True,
            )
            doc_summaries[knowledge_id] = [
                DocumentSummaryItem(
                    id=doc.id,
                    name=doc.name,
                    slug=doc.slug,
                    updated_at=doc.updated_at,
                    content_updated_at=doc.content_updated_at,
                )
                for doc in sorted_docs[:limit]
            ]
        return doc_summaries

    def get_list_with_knowledge(
        self, user_id: int, keyword: Optional[str] = None
    ) -> List[KnowledgeGroupResponse]:
        """获取带知识库的分组列表"""
        from app.services.knowledge_service import KnowledgeService

        knowledge_service = KnowledgeService(self.db)
        groups = self.get_list_by_user_id(user_id)
        keyword = (keyword or "").strip().lower()

        relations = (
            self.db.query(KnowledgeGroupRelation)
            .filter(KnowledgeGroupRelation.user_id == user_id)
            .options(
                joinedload(KnowledgeGroupRelation.knowledge).joinedload(Knowledge.team)
            )
            .order_by(
                KnowledgeGroupRelation.order_index.asc(),
                KnowledgeGroupRelation.created_at.asc(),
            )
            .all()
        )

        items_by_group: dict[str, list] = {group.id: [] for group in groups}
        active_knowledge_ids: list[str] = []
        for relation in relations:
            knowledge = relation.knowledge
            if not knowledge or knowledge.deleted_at is not None:
                continue
            if keyword and keyword not in (knowledge.name or "").lower():
                continue
            active_knowledge_ids.append(knowledge.id)

        doc_counts: dict[str, int] = {}
        if active_knowledge_ids:
            count_rows = (
                self.db.query(Document.knowledge_id, func.count(Document.id))
                .filter(Document.knowledge_id.in_(active_knowledge_ids))
                .group_by(Document.knowledge_id)
                .all()
            )
            doc_counts = {kid: cnt for kid, cnt in count_rows}

        # 批量获取文档top3
        doc_summaries = self._build_doc_summaries(
            relations, groups, active_knowledge_ids, limit=3
        )

        for relation in relations:
            knowledge = relation.knowledge
            if not knowledge or knowledge.deleted_at is not None:
                continue
            if keyword and keyword not in (knowledge.name or "").lower():
                continue
            response = knowledge_service.to_wrap_knowledge_response(knowledge, user_id)
            response = KnowledgeInGroupItem(
                **response.model_dump(),
                order_index=relation.order_index,
                relation_id=relation.id,
                doc_summary=doc_summaries.get(knowledge.id, []),
                doc_count=doc_counts.get(knowledge.id, 0),
            )
            items_by_group.setdefault(relation.group_id, []).append(response)

        result: List[KnowledgeGroupResponse] = []
        for group in groups:
            display_config = group.display_config or DEFAULT_DISPLAY_CONFIG.model_dump()
            result.append(
                KnowledgeGroupResponse(
                    id=group.id,
                    user_id=group.user_id,
                    group_name=group.group_name,
                    order_index=group.order_index,
                    is_default=group.is_default,
                    display_config=display_config,
                    created_at=group.created_at,
                    updated_at=group.updated_at,
                    knowledge_group_items=items_by_group.get(group.id, []),
                )
            )
        return result

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
