"""数据库混入类"""
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import Query
from datetime import datetime

class SoftDeleteMixin:
    """数据库混入类"""

    deleted_at = Column[datetime](DateTime, nullable=True, comment="删除时间(NULL表示未删除)")

    def soft_delete(self):
        """软删除"""
        self.deleted_at = datetime.now()

    @classmethod
    def filter_active(cls, query: Query):
        """过滤未删除的数据"""
        return query.filter(cls.deleted_at.is_(None))

    @classmethod
    def filter_deleted(cls, query: Query):
        """过滤已删除的数据"""
        return query.filter(cls.deleted_at.isnot(None))