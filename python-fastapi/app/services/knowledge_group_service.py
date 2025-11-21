"""知识库分组服务"""
from sqlalchemy.orm.session import Session
from app.schemas.knowledge_group import KnowledgeGroupCreate, KnowledgeGroupUpdate
from app.models.knowledge_group import KnowledgeGroup
from typing import List
from fastapi import HTTPException
class KnowledgeGroupService:
    """知识库分组服务"""
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, knowledge_group_in: KnowledgeGroupCreate) -> KnowledgeGroup:
        """创建知识库分组"""
        knowledge_group = KnowledgeGroup(
            user_id=knowledge_group_in.user_id,
            is_default=knowledge_group_in.is_default,
            group_name=knowledge_group_in.group_name,
            order_index=knowledge_group_in.order_index,
        )
        self.db.add(knowledge_group)
        self.db.commit()
        self.db.refresh(knowledge_group)
        return knowledge_group

    def get_list_by_user_id(self, user_id: int) -> List[KnowledgeGroup]:
        """获取知识库分组列表"""
        return self.db.query(KnowledgeGroup).filter(KnowledgeGroup.user_id == user_id).all()

        
    def update(self, group_id: int, knowledge_group_in: KnowledgeGroupUpdate) -> KnowledgeGroup:
        """更新知识库分组"""
        knowledge_group = self.db.query(KnowledgeGroup).filter(KnowledgeGroup.id == group_id).first()
        if not knowledge_group:
            raise HTTPException(status_code=404, detail="知识库分组不存在")
        knowledge_group.group_name = knowledge_group_in.group_name
        knowledge_group.order_index = knowledge_group_in.order_index
        knowledge_group.is_default = knowledge_group_in.is_default
        self.db.commit()
        self.db.refresh(knowledge_group)
        return knowledge_group