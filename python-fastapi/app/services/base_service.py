"""基础服务类"""

from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic
from app.core.mixins import SoftDeleteMixin

ModelType = TypeVar('ModelType', bound=SoftDeleteMixin)
class BaseService(Generic[ModelType]):
    """基础服务类"""

    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_active_query(self):
        """获取所有未删除的数据"""
        return self.model.filter_active(self.db.query(self.model))

    def get_deleted_query(self):
        """获取所有已删除的数据"""
        return self.model.filter_deleted(self.db.query(self.model))

    def get_all_query(self, include_deleted: bool = True):
        """获取所有记录查询数据"""
        query = self.db.query(self.model)
        if not include_deleted:
            query = self.model.filter_active(query)
        return query