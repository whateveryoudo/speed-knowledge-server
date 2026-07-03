from app.schemas.search import SearchQuery
from fastapi import HTTPException
from app.schemas.search import SearchContextType, SearchVisibilityType
from typing import List
from app.schemas.search import (
    SearchSection,
    SearchResponse,
    SearchKnowledgeItem,
    SearchDocumentItem,
)
from app.services.knowledge_service import KnowledgeService
from sqlalchemy.orm.session import Session
from app.models.knowledge import Knowledge
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from app.models.document import Document
from app.models.collaborator import Collaborator
from app.common.enums import CollaboratorStatus, CollaborateResourceType
from app.services.permission_service import PermissionService


class SearchService:
    KNOWLEDGE_LIMIT = 10
    DOCUMENT_LIMIT = 20

    def __init__(self, db: Session):
        self.db = db
        self.knowledge_service = KnowledgeService(db)

    def _get_collaborator_knowledge_ids(self, user_id: int) -> List[int]:
        """根据用户id查询协同表中符合的知识库id集合"""
        return [
            row.knowledge_id
            for row in self.db.query(Collaborator)
            .filter(
                Collaborator.user_id == user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                Collaborator.target_type == CollaborateResourceType.KNOWLEDGE.value,
                Collaborator.knowledge_id.isnot(None),
            )
            .distinct()
            .all()
        ]

    def _to_knowledge_item(self, row: Knowledge) -> SearchKnowledgeItem:
        """将知识库对象转换为搜索知识库项"""
        return SearchKnowledgeItem(
            id=row.id,
            name=row.name,
            slug=row.slug,
            team_slug=row.team.slug if row.team else None,
            is_public=bool(row.is_public),
        )

    def _search_knowledge_by_title(
        self,
        user_id: int,
        keyword: str,
        visibility: SearchVisibilityType,
        *,
        limit: int,
    ) -> List[SearchKnowledgeItem]:
        """根据标题搜索知识库"""
        # 构建查询条件
        query = (
            self.db.query(Knowledge)
            .options(joinedload(Knowledge.team))
            .filter(
                Knowledge.deleted_at.is_(None), Knowledge.name.ilike(f"%{keyword}%")
            )
        )

        # 如果是公开知识库（仅查询公开知识库）
        if visibility == SearchVisibilityType.PUBLIC:
            query = query.filter(Knowledge.is_public.is_(True))
        else:
            # 根据用户id查询协同表中符合的知识库
            accessible_ids = self._get_collaborator_knowledge_ids(user_id)
            print(f"accessible_ids: {accessible_ids}")
            if not accessible_ids:
                return []
            query = query.filter(Knowledge.id.in_(accessible_ids))

        rows = query.order_by(Knowledge.updated_at.desc()).limit(limit).all()
        # 对结果进行处理
        return [self._to_knowledge_item(row) for row in rows]

    def   _get_collaborator_document_ids(self, user_id: int) -> List[int]:
        """根据用户id查询协同表中符合的文档id集合"""
        return [
            row.document_id
            for row in self.db.query(Collaborator)
            .filter(
                Collaborator.user_id == user_id,
                Collaborator.status == CollaboratorStatus.ACCEPTED,
                Collaborator.target_type == CollaborateResourceType.DOCUMENT,
                Collaborator.document_id.isnot(None),
            )
            .distinct()
            .all()
        ]

    def _to_document_item(self, row: Document) -> SearchDocumentItem:
        """将文档对象转换为搜索文档项"""
        return SearchDocumentItem(
            id=row.id,
            name=row.name,
            slug=row.slug,
            knowledge_id=row.knowledge_id,
            knowledge_name=row.knowledge.name,
            knowledge_slug=row.knowledge.slug,
            team_slug=row.knowledge.team.slug if row.knowledge.team else None,
        )

    def _search_document_by_title(
        self,
        user_id: int,
        keyword: str,
        visibility: SearchVisibilityType,
        *,
        limit: int,
    ) -> List[SearchDocumentItem]:
        """根据标题搜索文档"""
        query = (
            self.db.query(Document)
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .options(joinedload(Document.knowledge).joinedload(Knowledge.team))
            .filter(
                Knowledge.deleted_at.is_(None),
                Document.deleted_at.is_(None),
                Document.name.ilike(f"%{keyword}%"),
            )
        )
        print(f"user_id: {user_id}")
        print(f"keyword: {keyword}")
        if visibility == SearchVisibilityType.PUBLIC:
            query = query.filter(
                or_(Document.is_public.is_(True), Knowledge.is_public.is_(True))
            )
        else:
            # 注意：这里有点特别的，需要整合两部分系统（因为系统含有知识库邀请和文档邀请（如果仅被邀请知识库，他也有所有文档的权限（会带有继承）））
            conditions = []
            accessible_kb_ids = self._get_collaborator_knowledge_ids(user_id)
            if accessible_kb_ids:
                conditions.append(Document.knowledge_id.in_(accessible_kb_ids))

            accessible_doc_ids = self._get_collaborator_document_ids(user_id)
            if accessible_doc_ids:
                conditions.append(Document.id.in_(accessible_doc_ids))
            if not conditions:
                # 如果没有资源，则不进行搜索
                return []
            query = query.filter(or_(*conditions))

        rows = query.order_by(Document.updated_at.desc()).limit(limit).all()
        # 对结果进行处理
        return [self._to_document_item(row) for row in rows]

    def _search_global(
        self, user_id: int, keyword: str, visibility: SearchVisibilityType
    ):
        """全局搜索（外层的（还是自己的知识库和文章））"""
        sections: List[SearchSection] = []

        # 搜索知识库

        kb_items = self._search_knowledge_by_title(
            user_id, keyword, visibility, limit=self.KNOWLEDGE_LIMIT
        )
        if kb_items:
            sections.append(SearchSection(type="knowledge", items=kb_items))

        # 文档搜索

        doc_items = self._search_document_by_title(
            user_id, keyword, visibility, limit=self.DOCUMENT_LIMIT
        )
        if doc_items:
            sections.append(SearchSection(type="document", items=doc_items))

        return SearchResponse(sections=sections)

    def _assert_knowledge_readable(self, user_id: int, knowledge_id: str):
        """知识库可读判断"""
        return PermissionService(self.db).assert_knowledge_readable(
            user_id, knowledge_id
        )

    def _search_document_in_knowledge(
        self, keyword: str, knowledge_id: str, limit: int
    ) -> List[SearchDocumentItem]:
        """在知识库内搜索文档"""

        rows = (
            self.db.query(Document)
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .options(joinedload(Document.knowledge).joinedload(Knowledge.team))
            .filter(
                Document.knowledge_id == knowledge_id,
                Document.deleted_at.is_(None),
                Knowledge.deleted_at.is_(None),
                Document.name.ilike(f"%{keyword}%"),
            )
            .order_by(Document.content_updated_at.desc())
            .limit(limit)
            .all()
        )

        return [self._to_document_item(row) for row in rows]

    def _search_in_knowledge(
        self, user_id: int, keyword: str, knowledge_id: str
    ) -> SearchResponse:
        """在知识库内搜索"""
        knowledge = self._assert_knowledge_readable(user_id, knowledge_id)

        doc_items = self._search_document_in_knowledge(
            keyword, knowledge.id, limit=self.DOCUMENT_LIMIT
        )
        sections: List[SearchSection] = []
        if doc_items:
            sections.append(SearchSection(type="document", items=doc_items))

        return SearchResponse(sections=sections)

    def search(self, user_id: int, query_in: SearchQuery) -> SearchResponse:
        keyword = (query_in.keyword or "").strip()
        if not keyword:
            raise HTTPException(status_code=400, detail="Keyword is required")

        if query_in.context == SearchContextType.GLOBAL:
            return self._search_global(user_id, keyword, query_in.visibility)

        if not query_in.knowledge_id:
            raise HTTPException(
                status_code=400, detail="知识库内搜索时，knowledge_id必传"
            )

        return self._search_in_knowledge(user_id, keyword, query_in.knowledge_id)
