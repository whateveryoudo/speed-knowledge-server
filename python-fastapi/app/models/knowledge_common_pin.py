from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid


class KnowledgeCommonPin(Base):
    """常用知识库pin表"""

    __tablename__ = "knowledge_common_pin"

    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uix_user_knowledge"),
    )
    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    knowledge_id = Column[str](
        String(36), ForeignKey("knowledge_base.id"), index=True, comment="知识库ID"
    )
    user_id = Column[int](Integer, ForeignKey("user.id"), index=True, comment="用户ID")
    order_index = Column[int](Integer, default=0, comment="排序索引")
    created_at = Column[datetime](DateTime, default=func.now(), comment="创建时间")
    updated_at = Column[datetime](
        DateTime, default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    user = relationship("User", back_populates="knowledge_common_pins")
    knowledge = relationship("Knowledge", back_populates="knowledge_common_pins")



