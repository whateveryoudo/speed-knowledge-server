from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import func, Integer, ForeignKey, DateTime, String, text
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class KnowledgeGroupRelation(Base):
    __tablename__ = "knowledge_group_relation"
    __table_args__ = (
        UniqueConstraint("group_id", "knowledge_id", name="uix_group_knowledge"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    knowledge_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_base.id"), nullable=False
    )
    group_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_group.id"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0"), nullable=True, comment="排序索引"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True, comment="更新时间"
    )

    knowledge = relationship("Knowledge", back_populates="group_relations")
    group = relationship("KnowledgeGroup", back_populates="group_relations")
