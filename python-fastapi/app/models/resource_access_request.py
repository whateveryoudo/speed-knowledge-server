"""资源访问申请（替换之前collaboration的资源相关逻辑）"""

from app.db.base import Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    func,
    Index,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.common.enums import ResourceType, AccessRequestStatus, ResourceRole
from datetime import datetime
import uuid


class ResourceAccessRequest(Base):
    __tablename__ = "resource_access_request"
    __table_args__ = (
        Index(
            "idx_access_request_resource_status",
            "resource_type",
            "resource_id",
            "status",
        ),
        Index(
            "idx_access_request_applicant_resource",
            "applicant_user_id",
            "resource_type",
            "resource_id",
        ),
    )
    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    resource_type = Column[ResourceType](String(30), comment="资源类型", nullable=False)
    resource_id = Column[str](String(36), comment="资源ID", nullable=False)
    request_role = Column[ResourceRole](
        Integer, comment="请求申请的角色", nullable=False
    )
    applicant_user_id = Column[int](Integer, comment="用户ID", nullable=False)
    invitation_id = Column[str](
        String(36),
        ForeignKey("invitation.id", ondelete="RESTRICT"),
        comment="邀请ID",
        nullable=True,
    )
    status = Column[AccessRequestStatus](
        Integer,
        comment="状态",
        nullable=False,
        default=AccessRequestStatus.PENDING.value,
    )
    reviewed_by = Column[int](
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        comment="审核用户ID",
        nullable=True,
    )
    reviewed_at = Column[datetime](DateTime, comment="审核时间", nullable=True)
    apply_message = Column[str](String(255), comment="申请说明", nullable=True)
    created_at = Column[datetime](DateTime, default=func.now(), comment="申请时间")
    updated_at = Column[datetime](
        DateTime, default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    applicant = relationship(
        "User", foreign_keys=[applicant_user_id], back_populates="access_requests"
    )
    reviewed_user = relationship(
        "User", foreign_keys=[reviewed_by], back_populates="reviewed_access_requests"
    )
    invitation = relationship(
        "Invitation",
        foreign_keys=[invitation_id],
        back_populates="access_requests",
    )
