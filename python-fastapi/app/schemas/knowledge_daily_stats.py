from pydantic import BaseModel, Field
from datetime import date, datetime
from app.common.enums import KnowledgeIndexPageLayout, KnowledgeIndexPageSort
class KnowledgeDailyStatsResponse(BaseModel):
    """知识库每日统计响应结构"""
    id: str = Field(..., description="ID")
    knowledge_id: str = Field(..., description="知识库ID")
    stats_date: date = Field(..., description="统计日期")
    word_count: int = Field(..., description="字数")

    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True