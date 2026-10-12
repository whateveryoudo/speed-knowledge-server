from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, func, ForeignKey, Integer
from app.db.base import Base
from app.core.mixins import SoftDeleteMixin
from sqlalchemy.orm import relationship, Mapped, mapped_column


class SpaceDept(SoftDeleteMixin, Base):
    """空间部门表"""

    __tablename__ = "space_dept"

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    space_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("space.id"), nullable=False, comment="所属空间ID"
    )
    name: Mapped[str] = mapped_column(String(30), nullable=False, comment="部门名称")
    order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="排序"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="更新时间",
    )

    team_members = relationship("TeamMember", back_populates="space_dept")