from sqlalchemy import Column, func, Integer, ForeignKey, DateTime, String, text
from app.db.base import Base
from datetime import datetime
from sqlalchemy.schema import UniqueConstraint
import uuid
from sqlalchemy.orm import relationship
class KnowledgeGroupRelation(Base):
    __tablename__ = "knowledge_group_relation"
    __table_args__ = (
        UniqueConstraint("user_id", "knowledge_id", name="uix_user_knowledge"),
        UniqueConstraint( "group_id", "knowledge_id", name="uix_group_knowledge"),
    )
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_id = Column(String(36), ForeignKey("knowledge_base.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    group_id = Column(String(36), ForeignKey("knowledge_group.id"))
    order_index = Column(Integer, default=0, server_default=text('0'), comment="排序索引")
    created_at = Column[datetime](DateTime, default=func.now(), comment="创建时间")
    updated_at = Column[datetime](DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    user = relationship("User", back_populates="knowledge_group_relations")
    knowledge = relationship("Knowledge", back_populates="group_relations")
    group = relationship("KnowledgeGroup", back_populates="group_relations")