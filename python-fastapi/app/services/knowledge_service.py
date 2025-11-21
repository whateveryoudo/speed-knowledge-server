"""知识库服务"""

from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge
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

    def create(self, knowledge_in: KnowledgeCreate) -> None:
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

        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        return knowledge

    def get_by_id(self, knowledge_id: int):
        """通过知识库id查询知识库"""
        return self.db.query(Knowledge).filter(Knowledge.id == knowledge_id).first()

    def get_list_by_user_id(self, user_id: int) -> List[Knowledge]:
        """通过用户id查询知识库列表"""
        return self.db.query(Knowledge).filter(Knowledge.user_id == user_id).all()
