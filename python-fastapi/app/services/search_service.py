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
from sqlalchemy.orm.session import Session
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.services.permission_service import PermissionService
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.document_repository import DocumentRepository


class SearchService:
    KNOWLEDGE_LIMIT = 10
    DOCUMENT_LIMIT = 20

    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)
        self.knowledge_repository = KnowledgeRepository(db)
        self.document_repository = DocumentRepository(db)

    def _to_knowledge_item(self, row: Knowledge) -> SearchKnowledgeItem:
        """将知识库对象转换为搜索知识库项"""
        return SearchKnowledgeItem(
            id=row.id,
            name=row.name,
            slug=row.slug,
            team_slug=row.team.slug if row.team else None,
            visibility=row.visibility,
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
        rows = self.knowledge_repository.list_active_by_title(keyword=keyword)

        permission_user_id = (
            None if visibility == SearchVisibilityType.PUBLIC else user_id
        )
        readable_rows = self.permission_service.filter_readable_knowledges(
            user_id=permission_user_id, knowledges=rows
        )
        # 对结果进行处理
        return [self._to_knowledge_item(row) for row in readable_rows[:limit]]

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
        rows = self.document_repository.list_active_by_title(keyword=keyword)
        permission_user_id = (
            None if visibility == SearchVisibilityType.PUBLIC else user_id
        )
        readable_rows = self.permission_service.filter_readable_documents(
            user_id=permission_user_id, documents=rows
        )
        # 对结果进行处理
        return [self._to_document_item(row) for row in readable_rows[:limit]]

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
        return self.permission_service.assert_knowledge_readable(user_id, knowledge_id)

    def _search_document_in_knowledge(
        self, *, user_id: int, keyword: str, knowledge_id: str, limit: int
    ) -> List[SearchDocumentItem]:
        """在知识库内搜索文档(带上用户权限)"""
        rows = self.document_repository.list_active_by_title(
            keyword=keyword, knowledge_id=knowledge_id, order_by_content_updated=True
        )

        readable_rows = self.permission_service.filter_readable_documents(
            user_id=user_id, documents=rows
        )

        return [self._to_document_item(row) for row in readable_rows[:limit]]

    def _search_in_knowledge(
        self, user_id: int, keyword: str, knowledge_id: str
    ) -> SearchResponse:
        """在知识库内搜索"""
        knowledge = self._assert_knowledge_readable(user_id, knowledge_id)

        doc_items = self._search_document_in_knowledge(
            user_id=user_id,
            keyword=keyword,
            knowledge_id=knowledge.id,
            limit=self.DOCUMENT_LIMIT,
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
