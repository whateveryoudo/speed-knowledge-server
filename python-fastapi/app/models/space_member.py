from warnings import deprecated
from app.db.base import Base
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey,func, Integer
from sqlalchemy.orm import relationship
from app.common.enums import SpaceMemberRole
import uuid
from app.core.mixins import SoftDeleteMixin
class SpaceMember(SoftDeleteMixin, Base):
    __tablename__ = "space_member"
    id = Column(String(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    space_id = Column(String(36), ForeignKey("space.id", ondelete="CASCADE"), nullable=False, comment="空间ID")
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    role = Column(Enum(SpaceMemberRole), nullable=False, comment="角色")
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.current_timestamp(), comment="更新时间")
    # dept_id = Column(String(36), ForeignKey("space_dept.id", ondelete="CASCADE"), nullable=True, comment="部门ID")

    space = relationship("Space", back_populates="space_members")
    user = relationship("User", back_populates="space_members")
    # space_dept = relationship("SpaceDept", back_populates="space_members")