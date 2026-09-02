from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    func,
    UniqueConstraint,
)
import uuid
from app.db.base import Base
from sqlalchemy.orm import relationship


class Collect(Base):
    """资源收藏(知识库/文档)"""

    __tablename__ = "collect"
    __table_args__ = (
        UniqueConstraint("user_id", "target_id", "target_type", name="uq_collect_user_target"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="用户ID",
    )
    target_type = Column(String(20), nullable=False, comment="目标资源类型")
    target_id = Column(
        String(36),
        nullable=False,
        comment="目标资源ID",
    )
    created_at: datetime = Column(
        DateTime, server_default=func.current_timestamp(), comment="创建时间"
    )
    updated_at: datetime = Column(
        DateTime,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )

    user = relationship("User", back_populates="collects")
