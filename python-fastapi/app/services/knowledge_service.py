"""知识库服务"""
from sqlalchemy.orm.session import Session
from app.schemas.knowledge import KnowledgeCreate
from app.models.knowledge import Knowledge

class KnowledgeService:
    """知识库服务
    """
    def __init__(self,db:Session) -> None:
        self.db = db

    def create(self, knowledge_in: KnowledgeCreate) -> str:
        """创建知识库"""
        # 默认isPublic为False
        knowledge = Knowledge(
            user_id=knowledge_in.user_id,
            name=knowledge_in.name,
            slug=knowledge_in.slug,
            description=knowledge_in.description,
        )
        self.db.add(knowledge)
        self.db.commit()
        return knowledge.id