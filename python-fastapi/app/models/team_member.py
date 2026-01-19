from app.db.base import Base
from app.core.mixins import SoftDeleteMixin
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func, Integer
import uuid
from app.common.enums import TeamMemberRole
from sqlalchemy.orm import relationship

class TeamMember(Base):
    """团队成员表"""
    __tablename__ = "team_member"
    id = Column(String(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    team_id = Column(String(36), ForeignKey("team.id", ondelete="CASCADE"), nullable=False, comment="团队ID")
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    role = Column(Enum(TeamMemberRole), nullable=False, comment="角色")
    dept_id = Column(String(36), ForeignKey("space_dept.id", ondelete="CASCADE"), nullable=True, comment="部门ID")
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="更新时间",
    )

    space_dept = relationship("SpaceDept", back_populates="team_members")
    team = relationship("Team", back_populates="team_members")
    user = relationship("User", back_populates="team_members")