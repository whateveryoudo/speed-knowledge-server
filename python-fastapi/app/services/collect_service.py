from app.models.collect import Collect
from app.common.enums import ResourceType
from sqlalchemy.orm import Session
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
from app.services.permission_service import PermissionService
from app.common.enums import CollectTargetType
from fastapi import HTTPException, status


class CollectService:
    """资源收藏服务(知识库/文档)"""

    _TARGET_RESOURCE_TYPE_MAP = {
        CollectTargetType.KNOWLEDGE: ResourceType.KNOWLEDGE,
        CollectTargetType.DOCUMENT: ResourceType.DOCUMENT,
    }

    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    @classmethod
    def _to_resource_type(cls, target_type: CollectTargetType) -> ResourceType:
        try:
            return cls._TARGET_RESOURCE_TYPE_MAP[target_type]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="暂不支持该收藏目标类型",
            )

    def get_collected_target_ids(
        self,
        *,
        user_id: int,
        target_type: CollectTargetType,
        target_ids: list[str],
    ) -> set[str]:
        """查询用户已收藏的目标ID集合"""
        unique_target_ids = list(dict.fromkeys(target_ids))
        if not unique_target_ids:
            return set()
        rows = (
            self.db.query(Collect.target_id)
            .filter(
                Collect.user_id == user_id,
                Collect.target_type == target_type.value,
                Collect.target_id.in_(unique_target_ids),
            )
            .all()
        )
        return {row.target_id for row in rows}

    def add_collect(
        self, *, user_id: int, target_type: CollectTargetType, target_id: str
    ):
        """添加资源收藏"""
        # 权限拦截(这里仅对只读进行拦截)
        resource_type = self._to_resource_type(target_type)
        self.permission_service.assert_resource_readable(
            user_id=user_id,
            resource_type=resource_type,
            identifier=target_id,
        )
        existing = self.check_is_collected(
            user_id=user_id, target_type=target_type, target_id=target_id
        )
        if existing is not None:
            return existing
        collect_orm_data = Collect(
            user_id=user_id,
            target_type=target_type.value,
            target_id=target_id,
        )
        self.db.add(collect_orm_data)
        self.db.commit()
        self.db.refresh(collect_orm_data)
        return collect_orm_data

    def get_collect(
        self, *, user_id: int, target_type: CollectTargetType, target_id: str
    ) -> Collect | None:
        """获取资源收藏"""
        return (
            self.db.query(Collect)
            .filter(
                Collect.user_id == user_id,
                Collect.target_type == target_type.value,
                Collect.target_id == target_id,
            )
            .first()
        )

    def remove_collect(
        self, *, user_id: int, target_type: CollectTargetType, target_id: str
    ) -> bool:
        """取消资源收藏"""
        collect = self.get_collect(
            user_id=user_id, target_type=target_type, target_id=target_id
        )
        if not collect:
            return False
        self.db.delete(collect)
        self.db.commit()
        return True

    def check_is_collected(
        self, *, user_id: int, target_type: CollectTargetType, target_id: str
    ) -> Collect | None:
        """检查资源是否收藏"""
        return self.get_collect(
            user_id=user_id, target_type=target_type, target_id=target_id
        )

    def _query_knowledge_collects(
        self, *, user_id: int, keyword: Optional[str] = None
    ) -> list[tuple[Collect, Knowledge]]:
        query = (
            self.db.query(Collect)
            .join(Knowledge, Collect.target_id == Knowledge.id)
            .filter(
                Collect.user_id == user_id,
                Collect.target_type == CollectTargetType.KNOWLEDGE.value,
            )
        )
        if keyword:
            query = query.filter(Knowledge.name.like(f"%{keyword}%"))
        collects = query.order_by(Collect.created_at.desc()).all()
        readable_knowledge_by_id = {
            knowledge.id: knowledge
            for knowledge in self.permission_service.list_readable_knowledges_by_ids(
                user_id=user_id,
                knowledge_ids=[collect.target_id for collect in collects],
            )
        }
        return [
            (collect, readable_knowledge_by_id[collect.target_id])
            for collect in collects
            if collect.target_id in readable_knowledge_by_id
        ]

    def _query_document_collects(
        self, *, user_id: int, keyword: Optional[str] = None
    ) -> list[tuple[Collect, Document]]:
        query = (
            self.db.query(Collect)
            .join(Document, Collect.target_id == Document.id)
            .filter(
                Collect.user_id == user_id,
                Collect.target_type == CollectTargetType.DOCUMENT.value,
            )
        )
        if keyword:
            query = query.filter(Document.name.like(f"%{keyword}%"))
        collects = query.order_by(Collect.created_at.desc()).all()
        readable_document_by_id = {
            document.id: document
            for document in self.permission_service.list_readable_documents_by_ids(
                user_id=user_id,
                document_ids=[collect.target_id for collect in collects],
            )
        }

        return [
            (collect, readable_document_by_id[collect.target_id])
            for collect in collects
            if collect.target_id in readable_document_by_id
        ]

    @staticmethod
    def _build_team_brief(knowledge: Knowledge) -> Optional[CollectTeamBrief]:
        """构建团队简要信息"""
        team = knowledge.team
        if team is None:
            return None
        return CollectTeamBrief(name=team.name, slug=team.slug)

    def _to_knowledge_item(
        self,
        *,
        collect: Collect,
        knowledge: Knowledge,
    ) -> CollectListItemResponse:
        return CollectListItemResponse(
            id=collect.id,
            target_type=CollectTargetType(collect.target_type),
            target_id=collect.target_id,
            created_at=collect.created_at,
            team=self._build_team_brief(knowledge),
            knowledge=CollectKnowledgeBrief(
                id=knowledge.id,
                name=knowledge.name,
                slug=knowledge.slug,
                icon=knowledge.icon,
            ),
        )

    def _to_document_item(
        self,
        *,
        collect: Collect,
        document: Document,
    ) -> CollectListItemResponse:
        knowledge = document.knowledge

        return CollectListItemResponse(
            id=collect.id,
            target_type=CollectTargetType(collect.target_type),
            target_id=collect.target_id,
            created_at=collect.created_at,
            team=self._build_team_brief(knowledge),
            knowledge=CollectKnowledgeBrief(
                id=knowledge.id,
                name=knowledge.name,
                slug=knowledge.slug,
                icon=knowledge.icon,
            ),
            document=CollectDocumentBrief(
                id=document.id,
                name=document.name,
                slug=document.slug,
                type=document.type,
            ),
        )

    def get_collects(
        self, *, user_id: int, search_collect: CollectSearch
    ) -> list[CollectListItemResponse]:
        """获取资源收藏列表"""
        target_type = search_collect.target_type
        keyword = search_collect.keyword

        knowledge_rows: list[tuple[Collect, Knowledge]] = []
        document_rows: list[tuple[Collect, Document]] = []
        if target_type in (None, CollectTargetType.KNOWLEDGE):
            knowledge_rows = self._query_knowledge_collects(
                user_id=user_id, keyword=keyword
            )
        if target_type in (None, CollectTargetType.DOCUMENT):
            document_rows = self._query_document_collects(
                user_id=user_id, keyword=keyword
            )

        result = [
            self._to_knowledge_item(collect=collect, knowledge=knowledge)
            for collect, knowledge in knowledge_rows
        ]
        result.extend(
            self._to_document_item(collect=collect, document=document)
            for collect, document in document_rows
        )
        result.sort(key=lambda x: x.created_at, reverse=True)
        return result
