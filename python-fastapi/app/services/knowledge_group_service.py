"""知识库分组服务"""
from sqlalchemy.orm.session import Session
from app.schemas.knowledge_group import KnowledgeGroupCreate
from app.models.knowledge_group import KnowledgeGroup

class KnowledgeGroupService:
    """知识库分组服务"""
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, knowledge_group_in: KnowledgeGroupCreate) -> None:
        """创建知识库分组"""
        knowledge_group = KnowledgeGroup(
            user_id=knowledge_group_in.user_id,
        )