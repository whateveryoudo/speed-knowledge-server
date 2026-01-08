from sqlalchemy import (
    Column,
    String,
    Index,
    Integer,
    Date,
    DateTime,
    UniqueConstraint,
    func,
)

import uuid
from app.db.base import Base


class KnowledgeDailyStats(Base):
    __tablename__ = "knowledge_daily_stats"

    __table_args__ = (
        UniqueConstraint(
            "knowledge_id", "stats_date", name="uix_knowledge_id_stats_date"
        ),
        Index("idx_knowledge_id", "knowledge_id"),
        Index("idx_stats_date", "stats_date"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_id = Column(String(36), nullable=False)
    stats_date = Column(Date, nullable=False)
    word_count = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
