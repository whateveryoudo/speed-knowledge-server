"""知识库服务"""

from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge
from app.models.knowledge_collaborator import KnowledgeCollaborator
from sqlalchemy import or_, and_
from app.schemas.knowledge_collaborator import KnowledgeCollaboratorCreate
from app.services.knowledge_collaborator_service import KnowledgeCollaboratorService
from app.common.enums import KnowledgeCollaboratorStatus
from app.models.document import Document
from typing import List
import secrets
import string

alphabet = string.ascii_letters + string.digits


class KnowledgeService:
    """知识库服务"""

    def _generate_slug(self) -> str:
        """生成知识库短链"""
        return "".join(secrets.choice(alphabet) for _ in range(6))

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, knowledge_in: KnowledgeCreate) -> Knowledge:
        """创建知识库"""
        temp_slug = self._generate_slug()
        while self.db.query(Knowledge).filter(Knowledge.slug == temp_slug).first():
            temp_slug = self._generate_slug()
        # 默认isPublic为False
        knowledge = Knowledge(
            user_id=knowledge_in.user_id,
            name=knowledge_in.name,
            group_id=knowledge_in.group_id,
            icon=knowledge_in.icon,
            slug=temp_slug,
            description=knowledge_in.description,
        )
        # 追加默认协作者
        collaborator_service = KnowledgeCollaboratorService(self.db)
        collaborator_service.join_default_collaborator(KnowledgeCollaboratorCreate(
            user_id=knowledge_in.user_id,
            knowledge_id=knowledge.id,
        ))
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def get_by_id_or_slug(self, identifier: str) -> Knowledge:
        """通过知识库id/短链查询知识库(附带文档数量)"""
        knowledge = (
            self.db.query(Knowledge)
            .filter(
                or_(Knowledge.id == identifier, Knowledge.slug == identifier),
            )
            .first()
        )
        if knowledge:
            items_count = self.db.query(Document).filter(Document.knowledge_id == knowledge.id).count()
            knowledge.items_count = items_count
        return knowledge
    def get_list_by_user_id(self, user_id: int) -> List[Knowledge]:
        """通过用户id查询知识库列表"""
        # 新增逻辑，追加协作者知识库查询
        knowledge_list = (self.db.query(Knowledge)
                .outerjoin(KnowledgeCollaborator, and_(Knowledge.id == KnowledgeCollaborator.knowledge_id, KnowledgeCollaborator.user_id == user_id, KnowledgeCollaborator.status == KnowledgeCollaboratorStatus.ACCEPTED.value))
                .filter(or_(Knowledge.user_id == user_id, KnowledgeCollaborator.id.isnot(None)))
                .distinct()
                .all())
        return knowledge_list
