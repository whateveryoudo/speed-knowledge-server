from sqlalchemy import UniqueConstraint,func,text, DateTime, String, Integer, Boolean
from sqlalchemy.orm import relationship,Mapped,mapped_column
from datetime import datetime

from app.models.base import Base
import uuid

class OrgInvitation(Base):
    """组织邀请链接模型"""
    __tablename__ = 'org_invitation'
    #  这里唯一键绑定多绑定了邀请人：同一空间下，单用户唯一
    __table_args__ = (
        UniqueConstraint(
            "org_type",
            "org_id",
            "inviter_id",
            name="uq_org_invitation_user",
            {
                "comment": "组织邀请链接配置"
            }
        )
    )

    id:Mapped[str] = mapped_column(String(36), primary_key=True,default=lambda: str(uuid.uuid4()) comment="主键ID")
    org_type:Mapped[str] = mapped_column(String(20), nullable=False, comment="组织类型：space - 空间，team-团队")
    org_id:Mapped[str] = mapped_column(String(36), nullable=False, index=True, comment="所属组织ID")
    inviter_id:Mapped[int] = mapped_column(Integer,, nullable=True, comment="邀请人ID（关联 user 表）")
    token:Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="邀请凭证")
    need_approval: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
        comment="是否需要审批",
    )
    default_dept_id:Mapped[str] = mapped_column(String(36),nullable=True,comment="空间邀请默认进入的部门ID")
    default_role: Mapped[str] = mapped_column(String(36), nullable=False,default="member", server_default="member", comment="受邀请后的默认角色")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        comment="邀请链接状态:active-正常,revoked-已撤销",
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
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )
    # 关系
    join_requests = relationship("OrgJoinRequest", foreign_keys="OrgJoinRequest.invitation_id",back_populates="invitation", cascade="all,delete-orphan")
    inviter = relationship("User", foreign_keys=[inviter_id])
  