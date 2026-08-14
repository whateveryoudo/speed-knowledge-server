"""文档数据访问"""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, Query
from app.models.document import Document
from app.models.knowledge import Knowledge
from app.repositories.base_repository import SoftDeleteRepository
from typing import Sequence


class DocumentRepository(SoftDeleteRepository[Document]):
    """仅提供数据库层面的读写"""

    def __init__(self, db: Session):
        super().__init__(db, Document)

    @staticmethod
    def _has_active_knowledge(document: Document | None) -> Document | None:
        if document is None:
            return None
        if document.knowledge is None or document.knowledge.deleted_at is not None:
            return None
        return document

    def _with_knowledge_scope(self, query: Query) -> Query:
        return query.options(
            joinedload(Document.knowledge).joinedload(Knowledge.space),
            joinedload(Document.knowledge).joinedload(Knowledge.team),
        )

    def get_active_by_id_or_slug(self, identifier: str) -> Document | None:
        """通过ID或slug获取未删除的文档"""
        document = self._with_knowledge_scope(
            self.active_query().filter(
                or_(Document.id == identifier, Document.slug == identifier)
            )
        ).first()
        return self._has_active_knowledge(document)

    def get_active_by_id(self, document_id: str) -> Document | None:
        """通过ID获取未删除的文档"""
        document = self._with_knowledge_scope(
            self.active_query().filter(Document.id == document_id)
        ).first()

        return self._has_active_knowledge(document)

    def exists_active_slug(self, *, knowledge_id: str, slug: str) -> bool:
        """检查指定知识库下是否存在未删除的文档slug"""
        return (
            self.active_query()
            .filter(Document.knowledge_id == knowledge_id, Document.slug == slug)
            .first()
            is not None
        )

    def list_active_by_knowledge(self, knowledge_id: str) -> list[Document]:
        """获取未删除的指定知识库下的文档列表"""
        return self.active_query().filter(Document.knowledge_id == knowledge_id).all()

    def list_active_by_ids(self, document_ids: Sequence[str]) -> list[Document]:
        """获取未删除的指定文档ID列表"""
        if not document_ids:
            return []
        documents = self._with_knowledge_scope(
            self.active_query().filter(Document.id.in_(document_ids))
        ).all()
        return [
            document
            for document in documents
            if self._has_active_knowledge(document) is not None
        ]

    def active_list_query(self) -> Query:
        """列表查询入口"""
        return self._with_knowledge_scope(self.active_query())
