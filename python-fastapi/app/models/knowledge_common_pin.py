from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class KnowledgeCommonPin(Base):
    """常用知识库pin表"""

    __tablename__ = "knowledge_common_pin"

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uix_user_knowledge"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    knowledge_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("knowledge_base.id"), index=True, nullable=True, comment="知识库ID"
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user.id"), index=True, nullable=True, comment="用户ID"
    )
    order_index: Mapped[Optional[int]] = mapped_column(
        Integer, default=0, nullable=True, comment="排序索引"
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), nullable=True, comment="创建时间"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True, comment="更新时间"
    )

    user = relationship("User", back_populates="knowledge_common_pins")
    knowledge = relationship("Knowledge", back_populates="knowledge_common_pins")
