from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, Enum, ForeignKey, func, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from app.common.enums import TeamMemberRole


class TeamMember(Base):
    """团队成员表"""

    __tablename__ = "team_member"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uix_team_member_team_user"),
    )

    id: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), primary_key=True
    )
    team_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        comment="团队ID",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    role: Mapped[TeamMemberRole] = mapped_column(
        Enum(TeamMemberRole), nullable=False, comment="角色"
    )
    dept_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("space_dept.id", ondelete="CASCADE"),
        nullable=True,
        comment="部门ID",
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

    space_dept = relationship("SpaceDept", back_populates="team_members")
    team = relationship("Team", back_populates="team_members")
    user = relationship("User", back_populates="team_members")
