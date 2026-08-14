"""知识库、文档资源邀请链接模型"""

from app.db.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func, Boolean
from datetime import datetime
import uuid
from sqlalchemy.sql import text
from sqlalchemy.schema import UniqueConstraint
from app.common.enums import InvitationStatus, ResourceType, ResourceRole
from sqlalchemy.orm import relationship


class ResourceInvitation(Base):
    """邀请链接模型(知识库、文档资源)"""

    __tablename__ = "resource_invitation"
    __table_args__ = (
        UniqueConstraint(
            "resource_type",
            "resource_id",
            name="uq_resource_invitation_resource",
        ),
    )

    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    resource_id = Column[str](
        String(36),
        nullable=False,
        comment="资源ID",
    )
    resource_type = Column[ResourceType](
        String(20),
        nullable=False,
        comment="资源类型:knowledge-知识库,document-文档",
    )

    inviter_id = Column[int](
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="邀请链接创建人",
    )

    token = Column[str](
        String(64), nullable=False, unique=True, comment="邀请链接token"
    )

    need_approval = Column[bool](
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
        comment="是否需要审批",
    )

    status = Column[InvitationStatus](
        String(20),
        nullable=False,
        default=InvitationStatus.ACTIVE.value,
        server_default=InvitationStatus.ACTIVE.value,
        comment="邀请状态:active-正常,revoked-已撤销",
    )
    offered_role = Column[ResourceRole](
        String(30),
        nullable=False,
        default=ResourceRole.READ.value,
        server_default=ResourceRole.READ.value,
        comment="邀请角色:read-只读,edit-可编辑,admin-管理员",
    )
    created_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at = Column[datetime](
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )

    inviter = relationship(
        "User", foreign_keys=[inviter_id], back_populates="created_resource_invitations"
    )
    access_requests = relationship(
        "ResourceAccessRequest",
        foreign_keys="ResourceAccessRequest.invitation_id",
        back_populates="invitation",
    )
