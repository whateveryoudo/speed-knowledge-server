"""知识库数据访问"""

from sqlalchemy import or_, func, and_
from sqlalchemy.orm import Session, contains_eager, Query
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.models.space import Space
from app.models.team import Team

from app.repositories.base_repository import SoftDeleteRepository
from typing import Sequence


class KnowledgeRepository(SoftDeleteRepository[Knowledge]):
    """仅提供数据库层面的读写"""

    def __init__(self, db: Session):
        super().__init__(db, Knowledge)

    def active_scope_query(self) -> Query:
        """知识库及其所属父资源均处于有效状态"""
        return (
            self.active_query()
            .join(Space, Space.id == Knowledge.space_id)
            .outerjoin(Team, Team.id == Knowledge.team_id)
            .options(contains_eager(Knowledge.space), contains_eager(Knowledge.team))
            .filter(
                Space.deleted_at.is_(None),
                or_(
                    Knowledge.team_id.is_(None),
                    and_(
                        Team.id.is_not(None),
                        Team.deleted_at.is_(None),
                        Team.space_id == Knowledge.space_id,
                    ),
                ),
            )
        )

    def get_active_by_id_or_slug(self, identifier: str) -> Knowledge | None:
        """通过ID或slug获取未删除的知识库"""
        return (
            self.active_scope_query()
            .filter(
                or_(Knowledge.id == identifier, Knowledge.slug == identifier),
            )
            .first()
        )

    def get_active_by_id(self, knowledge_id: str) -> Knowledge | None:
        """通过ID获取未删除的知识库"""
        return self.active_scope_query().filter(Knowledge.id == knowledge_id).first()

    def exists_slug(self, slug: str) -> bool:
        """检查全部知识库slug"""
        return self.all_query().filter(Knowledge.slug == slug).first() is not None

    def list_active_by_ids(self, knowledge_ids: Sequence[str]) -> list[Knowledge]:
        """获取未删除的知识库列表"""
        if not knowledge_ids:
            return []
        return self.active_scope_query().filter(Knowledge.id.in_(knowledge_ids)).all()

    def list_active_by_space_id(self, space_id: str) -> list[Knowledge]:
        """获取未删除的指定空间下的知识库列表"""
        return self.active_scope_query().filter(Knowledge.space_id == space_id).all()

    def list_active_by_team_id(self, team_id: str) -> list[Knowledge]:
        """获取未删除的指定团队下的知识库列表"""
        return self.active_scope_query().filter(Knowledge.team_id == team_id).all()

    def list_active_by_title(self, *, keyword: str) -> list[Knowledge]:
        """根据标题获取全部祖先链的有效知识库"""
        return (
            self.active_scope_query()
            .filter(Knowledge.name.ilike(f"%{keyword}%"))
            .order_by(Knowledge.updated_at.desc())
            .all()
        )

    def count_active_documents(self, knowledge_id: str) -> int:
        """获取未删除的指定知识库下的文档数量"""
        return (
            self.db.query(func.count(Document.id))
            .filter(
                Document.knowledge_id == knowledge_id, Document.deleted_at.is_(None)
            )
            .scalar()
            or 0
        )

    def active_list_query(self) -> Query:
        return self.active_scope_query()
