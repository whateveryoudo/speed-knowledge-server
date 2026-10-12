"""协同人员模型(知识库/文档)"""

from typing import Optional
from app.db.base import Base
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from app.common.enums import (
    CollaboratorRole,
    CollaboratorSource,
    CollaboratorStatus,
    CollaborateResourceType,
)


class Collaborator(Base):
    """协同人员模型(知识库/文档)"""

    __tablename__ = "collaborator"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    knowledge_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属知识库",
    )
    document_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属文档",
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="所属用户",
    )
    role: Mapped[CollaboratorRole] = mapped_column(
        Integer, nullable=False, comment="角色"
    )
    target_type: Mapped[CollaborateResourceType] = mapped_column(
        String(30), nullable=False, comment="目标类型:知识库/文档"
    )
    status: Mapped[CollaboratorStatus] = mapped_column(
        Integer,
        nullable=False,
        default=CollaboratorStatus.PENDING.value,
        comment="状态",
    )
    source: Mapped[CollaboratorSource] = mapped_column(
        Integer, nullable=False, comment="来源"
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

    user = relationship("User", back_populates="collaborators")
    knowledge = relationship("Knowledge", back_populates="collaborators")
    document = relationship("Document", back_populates="collaborators")
