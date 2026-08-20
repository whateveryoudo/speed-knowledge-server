"""文档数据访问"""

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, Query, contains_eager
from app.models.document import Document
from app.models.knowledge import Knowledge
from app.models.space import Space
from app.models.team import Team
from app.repositories.base_repository import SoftDeleteRepository
from typing import Sequence


class DocumentRepository(SoftDeleteRepository[Document]):
    """仅提供数据库层面的读写"""

    def __init__(self, db: Session):
        super().__init__(db, Document)

    def active_scope_query(self) -> Query:
        """文档及其所属知识库及其所属父资源均处于有效状态"""
        return (
            self.active_query()
            .join(Knowledge, Knowledge.id == Document.knowledge_id)
            .join(Space, Space.id == Knowledge.space_id)
            .outerjoin(Team, Team.id == Knowledge.team_id)
            .options(
                contains_eager(Document.knowledge).contains_eager(Knowledge.space),
                contains_eager(Document.knowledge).contains_eager(Knowledge.team),
            )
            .filter(
                Knowledge.deleted_at.is_(None),
                Space.deleted_at.is_(None),
                or_(
                    Knowledge.team_id.is_(None),
                    and_(
                        Team.deleted_at.is_(None), Team.space_id == Knowledge.space_id
                    ),
                ),
            )
        )

    def get_active_by_id_or_slug(self, identifier: str) -> Document | None:
        """通过ID或slug获取未删除的文档"""
        return (
            self.active_scope_query()
            .filter(or_(Document.id == identifier, Document.slug == identifier))
            .first()
        )

    def get_active_by_id(self, document_id: str) -> Document | None:
        """通过ID获取未删除的文档"""
        return self.active_scope_query().filter(Document.id == document_id).first()

    def exists_active_slug(self, *, knowledge_id: str, slug: str) -> bool:
        """检查指定知识库下是否存在未删除的文档slug"""
        return (
            self.active_query()
            .filter(Document.knowledge_id == knowledge_id, Document.slug == slug)
            .first()
            is not None
        )

    def list_active_by_knowledge(self, *, knowledge_id: str) -> list[Document]:
        """获取指定知识库下的有效文档，增加权限解析所需关系"""
        return (
            self.active_scope_query()
            .filter(Document.knowledge_id == knowledge_id)
            .all()
        )

    def list_active_by_ids(self, document_ids: Sequence[str]) -> list[Document]:
        """获取未删除的指定文档ID列表"""
        if not document_ids:
            return []
        return self.active_scope_query().filter(Document.id.in_(document_ids)).all()

    def active_list_query(self) -> Query:
        """列表查询入口"""
        return self.active_scope_query()
