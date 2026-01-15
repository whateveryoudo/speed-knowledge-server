"""知识库分组模型"""

from sqlalchemy import Column, Integer, BigInteger, String, JSON, text, Boolean, func, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.schemas.knowledge_group import DEFAULT_DISPLAY_CONFIG
import uuid
from app.core.mixins import SoftDeleteMixin
class KnowledgeGroup(SoftDeleteMixin, Base):
    """知识库分组模型"""

    __tablename__ = "knowledge_group"
    id = Column[str](String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True, comment="分组ID")
    user_id = Column[int](Integer, index=True, comment="用户ID")
    group_name = Column(String(255), default="新建分组", index=True, comment="分组名称")
    order_index = Column(Integer, default=0, server_default=text('0'), comment="排序索引")
    is_default = Column(Boolean, default=False, comment="是否默认分组")
    created_at = Column(DateTime, server_default=func.current_timestamp(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="更新时间")

    display_config = Column(JSON, default=DEFAULT_DISPLAY_CONFIG.model_dump(), nullable=True, comment="显示配置")
    knowledge_items = relationship("Knowledge", back_populates="group", cascade="all, delete")
    