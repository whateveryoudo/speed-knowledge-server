from datetime import datetime, date
import uuid
from sqlalchemy import (
    String,
    Index,
    Integer,
    Date,
    DateTime,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
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

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    knowledge_id: Mapped[str] = mapped_column(String(36), nullable=False)
    stats_date: Mapped[date] = mapped_column(Date, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
