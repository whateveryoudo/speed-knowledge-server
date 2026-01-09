from sqlalchemy.orm import Session
from app.models.knowledge_daily_stats import KnowledgeDailyStats
from typing import Optional
from datetime import date
class KnowledgeDailyStatsService:
    """知识库每日统计服务"""
    def __init__(self, db: Session):
        self.db = db

    def get_daily_stats_by_knowledge_id(self, knowledge_id: str, stats_date: Optional[date] = None) -> Optional[KnowledgeDailyStats]:
        """获取知识库某日统计(未传入则获取最近的统计数据)"""
        if stats_date:
            stats_data = self.db.query(KnowledgeDailyStats).filter(KnowledgeDailyStats.knowledge_id == knowledge_id, KnowledgeDailyStats.stats_date == stats_date).first()
        else:
            stats_data = self.db.query(KnowledgeDailyStats).filter(KnowledgeDailyStats.knowledge_id == knowledge_id).order_by(KnowledgeDailyStats.stats_date.desc()).first()
        return stats_data