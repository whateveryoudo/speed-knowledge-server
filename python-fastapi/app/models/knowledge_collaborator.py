"""知识库协同人员模型"""
from app.db.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from datetime import datetime
import uuid
from app.common.enums import KnowledgeCollaboratorRole, KnowledgeCollaboratorSource, KnowledgeCollaboratorStatus

class KnowledgeCollaborator(Base):
    """知识库协同人员模型"""
    __tablename__ = "knowledge_collaborator"

    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True, comment="主键")
    knowledge_id = Column[str](String(36), ForeignKey("knowledge_base.id", ondelete="CASCADE"), index=True, nullable=False, comment="所属知识库")
    user_id = Column[int](Integer, index=True, nullable=False, comment="所属用户")
    role = Column[KnowledgeCollaboratorRole](String(10), nullable=False, comment="角色")

    status = Column[KnowledgeCollaboratorStatus](Integer, nullable=False, default=KnowledgeCollaboratorStatus.PENDING.value, comment="状态")
    source = Column[KnowledgeCollaboratorSource](Integer, nullable=False, comment="来源")
    created_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column[datetime](DateTime, nullable=False, server_default=func.current_timestamp(), server_onupdate=func.current_timestamp(), comment="更新时间")
