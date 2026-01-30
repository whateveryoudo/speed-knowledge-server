"""知识库邀请链接模型"""

from app.db.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from datetime import datetime
import uuid
from app.common.enums import CollaboratorRole, InvitationStatus, CollaborateResourceType


class Invitation(Base):
    """邀请链接模型(知识库/文档)"""

    __tablename__ = "invitation"

    id = Column[str](
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="主键",
    )
    knowledge_id = Column[str](
        String(36),
        ForeignKey("knowledge_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属知识库",
    )
    document_id = Column[str](
        String(36),
        ForeignKey("document_base.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
        comment="所属文档",
    )
    inviter_id = Column[int](
        Integer, index=True, nullable=True, default=None, comment="被邀请用户id"
    )
    invitate_type = Column[CollaborateResourceType](
        String(20),
        nullable=False,
        default=CollaborateResourceType.KNOWLEDGE.value,
        comment="邀请来源:knowledge-知识库,document-文档",
    )
    token = Column[str](
        String(45), nullable=False, unique=True, comment="邀请链接token"
    )

    role = Column[CollaboratorRole](
        Integer,
        nullable=False,
        default=CollaboratorRole.READ.value,
        comment="角色",
    )
    need_approval = Column[int](
        Integer, nullable=True, default=0, comment="是否需要审批:0-否,1-是"
    )

    status = Column[InvitationStatus](
        Integer,
        nullable=False,
        default=InvitationStatus.ACTIVE.value,
        comment="状态:1-正常,2-已撤销",
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
