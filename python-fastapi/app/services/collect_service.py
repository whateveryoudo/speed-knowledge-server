from app.models.collect import Collect
from app.common.enums import CollectResourceType
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from app.schemas.collect import (
    CollectSearch,
    CollectListItemResponse,
    CollectTeamBrief,
    CollectKnowledgeBrief,
    CollectDocumentBrief,
)
from app.models.knowledge import Knowledge
from app.models.document import Document
from typing import Optional


class CollectService:
    """资源收藏服务(知识库/文档)"""

    def __init__(self, db: Session):
        self.db = db

    def add_collect(
        self, user_id: int, identifier: str, resource_type: CollectResourceType
    ):
        """添加资源收藏"""
        collect_orm_data = (
            Collect(
                user_id=user_id,
                resource_type=resource_type.value,
                knowledge_id=identifier,
            )
            if resource_type == CollectResourceType.KNOWLEDGE
            else Collect(
                user_id=user_id,
                resource_type=resource_type.value,
                document_id=identifier,
            )
        )
        self.db.add(collect_orm_data)
        self.db.commit()
        self.db.refresh(collect_orm_data)
        return collect_orm_data

    def remove_collect(
        self, user_id: int, identifier: str, resource_type: CollectResourceType
    ):
        """取消资源收藏"""
        collect = (
            self.db.query(Collect)
            .filter(
                Collect.user_id == user_id,
                or_(
                    Collect.knowledge_id == identifier,
                    Collect.document_id == identifier,
                ),
                Collect.resource_type == resource_type.value,
            )
            .first()
        )
        if not collect:
            return None
        self.db.delete(collect)
        self.db.commit()
        return None

    def check_is_collected(
        self, user_id: int, identifier: str, resource_type: CollectResourceType
    ):
        """检查资源是否收藏"""
        return (
            self.db.query(Collect)
            .filter(
                Collect.user_id == user_id,
                or_(
                    Collect.knowledge_id == identifier,
                    Collect.document_id == identifier,
                ),
                Collect.resource_type == resource_type.value,
            )
            .first()
        )

    def _query_knowledge_collects(self, user_id: int, keyword: Optional[str] = None):
        query = (
            self.db.query(Collect)
            .join(Knowledge, Collect.knowledge_id == Knowledge.id)
            .options(joinedload(Collect.knowledge).joinedload(Knowledge.team))
            .filter(
                Collect.user_id == user_id,
                Collect.resource_type == CollectResourceType.KNOWLEDGE.value,
                Knowledge.deleted_at.is_(None),
            )
        )
        if keyword:
            query = query.filter(Knowledge.name.like(f"%{keyword}%"))
        return query.order_by(Collect.created_at.desc()).all()

    def _query_document_collects(self, user_id: int, keyword: Optional[str] = None):
        query = (
            self.db.query(Collect)
            .join(Document, Collect.document_id == Document.id)
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .options(
                joinedload(Collect.document)
                .joinedload(Document.knowledge)
                .joinedload(Knowledge.team)
            )
            .filter(
                Collect.user_id == user_id,
                Collect.resource_type == CollectResourceType.DOCUMENT.value,
                Document.deleted_at.is_(None),
                Knowledge.deleted_at.is_(None),
            )
        )
        if keyword:
            query = query.filter(Document.name.like(f"%{keyword}%"))
        return query.order_by(Collect.created_at.desc()).all()

    def _to_list_item(self, collect: Collect) -> Optional[CollectListItemResponse]:
        """将收藏转换为列表项"""
        if collect.resource_type == CollectResourceType.KNOWLEDGE.value:
            knowledge = collect.knowledge
            if not knowledge or knowledge.deleted_at:
                return None
            team = knowledge.team
            if not team or team.deleted_at:
                return None
            return CollectListItemResponse(
                id=collect.id,
                resource_type=CollectResourceType(collect.resource_type),
                identifier=knowledge.id,
                created_at=collect.created_at,
                team=CollectTeamBrief(name=team.name, slug=team.slug),
                knowledge=CollectKnowledgeBrief(
                    name=knowledge.name,
                    slug=knowledge.slug,
                    icon=knowledge.icon,
                    id=knowledge.id,
                ),
            )
        document = collect.document
        if not document or document.deleted_at:
            return None

        knowledge = document.knowledge
        if not knowledge or knowledge.deleted_at:
            return None
        team = knowledge.team
        if not team or team.deleted_at:
            return None
        return CollectListItemResponse(
            id=collect.id,
            resource_type=CollectResourceType(collect.resource_type),
            identifier=document.id,
            created_at=collect.created_at,
            team=CollectTeamBrief(name=team.name, slug=team.slug),
            knowledge=CollectKnowledgeBrief(
                name=knowledge.name,
                slug=knowledge.slug,
                icon=knowledge.icon,
                id=knowledge.id,
            ),
            document=CollectDocumentBrief(
                name=document.name,
                slug=document.slug,
                id=document.id,
                type=document.type,
            ),
        )

    def get_collects(self, user_id: int, search_collect: CollectSearch):
        """获取资源收藏列表"""
        resource_type = search_collect.resource_type
        keyword = search_collect.keyword
        if resource_type == CollectResourceType.KNOWLEDGE:
            collects = self._query_knowledge_collects(user_id, keyword)
        elif resource_type == CollectResourceType.DOCUMENT:
            collects = self._query_document_collects(user_id, keyword)
        else:
            collects = self._query_knowledge_collects(
                user_id, keyword
            ) + self._query_document_collects(user_id, keyword)
            collects.sort(key=lambda x: x.created_at, reverse=True)
        result = []
        for collect in collects:
            list_item = self._to_list_item(collect)
            if list_item:
                result.append(list_item)
        return result
