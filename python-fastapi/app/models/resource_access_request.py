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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.common.enums import ResourceType, AccessRequestStatus, ResourceRole
from datetime import datetime
import uuid


class ResourceAccessRequest(Base):
    __tablename__ = "resource_access_request"
    __table_args__ = (
        UniqueConstraint(
            "pending_key",
            name="uq_resource_access_request_pending_key",
        ),
        Index(
            "idx_access_request_applicant_resource",
            "applicant_user_id",
            "resource_type",
            "resource_id",
        ),
        Index(
            "idx_access_request_resource_status",
            "resource_type",
            "resource_id",
            "status",
        ),
    )
    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    pending_key = Column[str](
        String(128),
        comment="待审批幂等键：仅pending状态时有值，审批结束后置空",
        nullable=True,
    )
    resource_type = Column[ResourceType](String(30), comment="资源类型", nullable=False)
    resource_id = Column[str](String(36), comment="资源ID", nullable=False)
    requested_role = Column[ResourceRole](
        String(30), comment="请求申请的角色", nullable=False
    )
    applicant_user_id = Column[int](
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT"),
        comment="用户ID",
        nullable=False,
        index=True,
    )
    invitation_id = Column[str](
        String(36),
        ForeignKey("resource_invitation.id", ondelete="RESTRICT"),
        comment="邀请ID",
        nullable=True,
    )
    status = Column[AccessRequestStatus](
        String(20),
        comment="状态",
        nullable=False,
        server_default=AccessRequestStatus.PENDING.value,
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
    created_at = Column[datetime](
        DateTime,
        default=func.now(),
        server_default=func.current_timestamp(),
        comment="申请时间",
    )
    updated_at = Column[datetime](
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )
    applicant = relationship(
        "User", foreign_keys=[applicant_user_id], back_populates="access_requests"
    )
    reviewed_user = relationship(
        "User", foreign_keys=[reviewed_by], back_populates="reviewed_access_requests"
    )
    invitation = relationship(
        "ResourceInvitation",
        foreign_keys=[invitation_id],
        back_populates="access_requests",
    )
