from app.models.collect import Collect
from app.common.enums import CollectResourceType
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.schemas.collect import CollectSearch
class CollectService:
    """资源收藏服务(知识库/文档)"""
    def __init__(self, db: Session):
        self.db = db

    def add_collect(self, user_id: str, identifier: str, resource_type: CollectResourceType):
        """添加资源收藏"""
        collect_orm_data = Collect(
                user_id=user_id,
                resource_type=resource_type,
                knowledge_id=identifier,
            ) if resource_type == CollectResourceType.KNOWLEDGE else Collect(
                user_id=user_id,
                resource_type=resource_type,
                document_id=identifier,
            )
        self.db.add(collect_orm_data)
        self.db.commit()
        self.db.refresh(collect_orm_data)
        return collect_orm_data

    def remove_collect(self, user_id: str, identifier: str, resource_type: CollectResourceType):
        """取消资源收藏"""
        collect = self.db.query(Collect).filter(Collect.user_id == user_id, or_(Collect.knowledge_id == identifier, Collect.document_id == identifier), Collect.resource_type == resource_type).first()
        self.db.delete(collect)
        self.db.commit()
        return None

    def check_is_collected(self, user_id: str, identifier: str, resource_type: CollectResourceType):
        """检查资源是否收藏"""
        return self.db.query(Collect).filter(Collect.user_id == user_id, or_(Collect.knowledge_id == identifier, Collect.document_id == identifier), Collect.resource_type == resource_type).first()

    def get_collects(self, user_id: str, search_collect: CollectSearch):
        """获取资源收藏列表"""
        return self.db.query(Collect).filter(Collect.user_id == user_id, and_(Collect.resource_type == search_collect.resource_type, Collect.knowledge_id.like(f"%{search_collect.keyword}%"), Collect.document_id.like(f"%{search_collect.keyword}%"))).all()