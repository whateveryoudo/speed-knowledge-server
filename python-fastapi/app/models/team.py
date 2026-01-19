from app.db.base import Base
from app.core.mixins import SoftDeleteMixin
from sqlalchemy import Column, String, DateTime, Integer, Enum, Boolean, func, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.common.enums import TeamVisibility
import uuid

class Team(SoftDeleteMixin, Base):
    """团队表（承载个人和团队空间）"""
    __tablename__ = "team"
    id = Column(String(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    name = Column(String(30), nullable=False, comment="团队名称")
    icon = Column(String(20), nullable=True, comment="团队图标(团队则为类型，个人则存放的是url链接)")
    slug = Column(String(64), index=True, nullable=False, unique=True, comment="团队标识(用于访问知识库的时候携带)")
    space_id = Column(String(36), ForeignKey("space.id", ondelete="CASCADE"), nullable=False, comment="空间ID")
    description = Column(String(512), nullable=True, comment="团队简介")
    visibility = Column(Enum(TeamVisibility), nullable=False, comment="团队可见性(公开给空间所有成员)")
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="更新时间")
    is_default = Column(Boolean, nullable=False, default=False, comment="是否为默认团队")
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="团队所有者ID")

    joined_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="加入时间")
    team_members = relationship("TeamMember", back_populates="team", cascade="all, delete")
    knowledge_items = relationship("Knowledge", back_populates="team", cascade="all, delete")