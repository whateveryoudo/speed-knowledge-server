from sqlalchemy import String, Integer, DateTime, Boolean , UniqueConstraint, func
from sqlalchemy.orm import relationship,Mapped,mapped_column
from typing import Optional
from datetime import datetime
from app.db.base import Base
import uuid

class OrgJoinRequest(Base):
    """组织邀请审批记录模型"""
    __tablename__ = 'org_join_request'
    # 防并发唯一键：pending时有值，结束后会清空
    __table_args__ = (
        UniqueConstraint("pending_key", name="uq_org_join_request_pending_key"),
    )

    id:Mapped[str] = mapped_column(String(36), primary_key=True,default=lambda: str(uuid.uuid4()), comment="主键ID")
    org_type:Mapped[str] = mapped_column(String(20), nullable=False, comment="组织类型：space - 空间，team-团队")
    org_id:Mapped[str] = mapped_column(String(36), nullable=False, index=True, comment="所属组织ID")
    applicant_user_id:Mapped[int]= mapped_column(Integer, nullable=False, comment="申请人用户ID")
    department_id:Mapped[str] = mapped_column(String(36),nullable=True,comment="申请加入目标部门ID")
    target_role:Mapped[str] = mapped_column(String(20),nullable=False,comment="申请加入目标角色")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
        default="pending",
        comment="状态:pending-待处理，approved-已批准，rejected-已拒绝"
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="审核用户ID",
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="审核时间",
        nullable=True,
    )
    apply_message: Mapped[Optional[str]] = mapped_column(
        String(255), comment="申请说明", nullable=True
    )
    # 并发幂等占位键（格式：{org_type}:{org_id}:{applicant_user_id}）
    pending_key: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="待审批幂等唯一键（排队时有值，终态置NULL）"
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
    applicant = relationship("User", foreign_keys=[applicant_user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
  